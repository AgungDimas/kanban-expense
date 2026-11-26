import csv
from decimal import Decimal
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch, ProtectedError, Sum

from .models import Wallet, Category, BoardColumn, ExpenseCard
from .serializers import (
    WalletSerializer,
    CategorySerializer,
    BoardColumnSerializer,
    ExpenseCardSerializer,
    MoveCardSerializer,
)
from .services import (
    get_default_user,
    move_card,
    create_card,
    delete_card,
    update_card,
)


class BoardView(APIView):
    """
    GET /api/board/
    Returns all board columns with their nested cards ordered by position.
    """

    def get(self, request, *args, **kwargs):
        cards_prefetch = Prefetch(
            "cards",
            queryset=ExpenseCard.objects.select_related("wallet", "category").order_by("position", "id"),
        )
        columns = BoardColumn.objects.prefetch_related(cards_prefetch).order_by("order", "id")
        serializer = BoardColumnSerializer(columns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletViewSet(viewsets.ModelViewSet):
    """
    GET /api/wallets/
    POST /api/wallets/
    PUT / PATCH /api/wallets/{id}/
    DELETE /api/wallets/{id}/
    """
    queryset = Wallet.objects.all().order_by("id")
    serializer_class = WalletSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else get_default_user()
        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_name = instance.name
        try:
            instance.delete()
            return Response(
                {"detail": f"Dompet '{wallet_name}' berhasil dihapus."},
                status=status.HTTP_200_OK,
            )
        except ProtectedError:
            card_count = instance.cards.count()
            return Response(
                {
                    "detail": f"Dompet '{wallet_name}' tidak dapat dihapus karena masih digunakan oleh {card_count} kartu pengeluaran. Pindahkan atau hapus kartu tersebut terlebih dahulu."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET /api/categories/
    POST /api/categories/
    PUT / PATCH /api/categories/{id}/
    DELETE /api/categories/{id}/
    """
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else get_default_user()
        serializer.save(user=user)


class ExpenseCardViewSet(viewsets.ModelViewSet):
    """
    Endpoints for Expense Cards:
    - GET /api/expenses/
    - POST /api/expenses/
    - GET /api/expenses/{id}/
    - PATCH / PUT /api/expenses/{id}/
    - DELETE /api/expenses/{id}/
    - PATCH /api/expenses/{id}/move/
    """
    queryset = ExpenseCard.objects.select_related("column", "wallet", "category").order_by("position", "id")
    serializer_class = ExpenseCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else get_default_user()
        card = create_card(serializer.validated_data, user=user)

        # Refresh wallet to send updated balance back to frontend
        wallet = Wallet.objects.get(id=card.wallet_id)

        response_data = self.get_serializer(card).data
        return Response(
            {
                "card": response_data,
                "wallet": WalletSerializer(wallet).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        card = update_card(instance.id, serializer.validated_data)
        wallet = Wallet.objects.get(id=card.wallet_id)

        return Response(
            {
                "card": self.get_serializer(card).data,
                "wallet": WalletSerializer(wallet).data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet = delete_card(instance.id)

        response_data = {"detail": "Kartu berhasil dihapus."}
        if wallet:
            response_data["wallet"] = WalletSerializer(wallet).data

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="move")
    def move(self, request, pk=None):
        """
        PATCH /api/expenses/{id}/move/
        Payload: { "target_column_id": 3, "new_position": 1500.0 }
        """
        serializer = MoveCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_column_id = serializer.validated_data["target_column_id"]
        new_position = serializer.validated_data["new_position"]

        card, wallet = move_card(
            card_id=pk,
            target_column_id=target_column_id,
            new_position=new_position,
        )

        return Response(
            {
                "card": ExpenseCardSerializer(card).data,
                "wallet": WalletSerializer(wallet).data,
            },
            status=status.HTTP_200_OK,
        )


class AnalyticsSummaryView(APIView):
    """
    GET /api/analytics/summary/
    Returns server-aggregated stats.
    """
    def get(self, request, *args, **kwargs):
        total_balance = Wallet.objects.aggregate(total=Sum("balance"))["total"] or Decimal("0.00")
        total_paid = ExpenseCard.objects.filter(column__deducts_balance=True).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        total_unpaid = ExpenseCard.objects.filter(column__deducts_balance=False).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        card_count = ExpenseCard.objects.count()

        return Response({
            "total_balance": total_balance,
            "total_paid": total_paid,
            "total_unpaid": total_unpaid,
            "card_count": card_count,
        }, status=status.HTTP_200_OK)


class ExportCSVView(APIView):
    """
    GET /api/export/
    Downloads all expenses formatted as a CSV file.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="kanban_expenses_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Judul",
            "Nominal",
            "Status / Kolom",
            "Dompet",
            "Kategori",
            "Jatuh Tempo",
            "Tanggal Lunas",
            "Catatan",
            "Dibuat Pada",
        ])

        cards = ExpenseCard.objects.select_related("column", "wallet", "category").order_by("id")
        for card in cards:
            writer.writerow([
                card.id,
                card.title,
                f"{card.amount:.2f}",
                card.column.name if card.column else "-",
                card.wallet.name if card.wallet else "-",
                card.category.name if card.category else "-",
                card.due_date.strftime("%Y-%m-%d") if card.due_date else "-",
                card.paid_at.strftime("%Y-%m-%d %H:%M") if card.paid_at else "-",
                card.notes,
                card.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        return response
