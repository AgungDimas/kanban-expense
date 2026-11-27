from decimal import Decimal
from rest_framework import serializers
from .models import Wallet, Category, BoardColumn, ExpenseCard
from .services import get_default_user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "name", "balance", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if "user" not in validated_data or not validated_data["user"]:
            request = self.context.get("request")
            user = request.user if request and request.user.is_authenticated else get_default_user()
            validated_data["user"] = user
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "monthly_budget", "color", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        if "user" not in validated_data or not validated_data["user"]:
            request = self.context.get("request")
            user = request.user if request and request.user.is_authenticated else get_default_user()
            validated_data["user"] = user
        return super().create(validated_data)


class ExpenseCardSerializer(serializers.ModelSerializer):
    wallet_name = serializers.CharField(source="wallet.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    category_color = serializers.CharField(source="category.color", read_only=True, default="#6B7280")
    column_name = serializers.CharField(source="column.name", read_only=True)

    class Meta:
        model = ExpenseCard
        fields = [
            "id",
            "title",
            "amount",
            "notes",
            "due_date",
            "paid_at",
            "position",
            "column",
            "column_name",
            "wallet",
            "wallet_name",
            "category",
            "category_name",
            "category_color",
            "created_at",
        ]
        read_only_fields = ["id", "paid_at", "created_at"]


class MoveCardSerializer(serializers.Serializer):
    target_column_id = serializers.IntegerField(required=True)
    new_position = serializers.FloatField(required=True)


class BoardColumnSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = BoardColumn
        fields = ["id", "name", "order", "deducts_balance", "cards", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_cards(self, obj):
        # Return cards ordered by position
        cards = obj.cards.all().select_related("wallet", "category").order_by("position", "id")
        return ExpenseCardSerializer(cards, many=True).data


class WalletTransferSerializer(serializers.Serializer):
    from_wallet_id = serializers.IntegerField(required=True)
    to_wallet_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True, min_value=Decimal("1.00"))
    notes = serializers.CharField(required=False, allow_blank=True, default="")

