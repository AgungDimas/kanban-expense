from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import BoardColumn, Wallet, Category, ExpenseCard

User = get_user_model()


class KanbanExpenseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")

        # Kolom
        self.col_wishlist = BoardColumn.objects.create(
            user=self.user, name="Wishlist", order=1, deducts_balance=False
        )
        self.col_unpaid = BoardColumn.objects.create(
            user=self.user, name="Tagihan", order=2, deducts_balance=False
        )
        self.col_paid = BoardColumn.objects.create(
            user=self.user, name="Lunas", order=3, deducts_balance=True
        )

        # Dompet
        self.wallet = Wallet.objects.create(
            user=self.user, name="Dompet Utama", balance=Decimal("100000.00")
        )

        # Kategori
        self.category = Category.objects.create(
            user=self.user, name="Kebutuhan", monthly_budget=Decimal("500000.00"), color="#3B82F6"
        )

    def test_get_board_structure(self):
        """Test GET /api/board/ returns nested cards in order."""
        card1 = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_wishlist,
            wallet=self.wallet,
            category=self.category,
            title="Card Pos 200",
            amount=Decimal("10000.00"),
            position=200.0,
        )
        card2 = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_wishlist,
            wallet=self.wallet,
            category=self.category,
            title="Card Pos 100",
            amount=Decimal("5000.00"),
            position=100.0,
        )

        response = self.client.get("/api/board/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # First column cards should be ordered by position: 100 first, then 200
        wishlist_col = next(c for c in response.data if c["id"] == self.col_wishlist.id)
        self.assertEqual(len(wishlist_col["cards"]), 2)
        self.assertEqual(wishlist_col["cards"][0]["id"], card2.id)
        self.assertEqual(wishlist_col["cards"][1]["id"], card1.id)

    def test_create_expense_unpaid_does_not_deduct_balance(self):
        """Creating card in deducts_balance=False should not deduct wallet."""
        payload = {
            "title": "Beli Buku",
            "amount": "25000.00",
            "column": self.col_wishlist.id,
            "wallet": self.wallet.id,
            "category": self.category.id,
        }
        response = self.client.post("/api/expenses/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))

        card = ExpenseCard.objects.get(id=response.data["card"]["id"])
        self.assertIsNone(card.paid_at)

    def test_create_expense_paid_deducts_balance(self):
        """Creating card directly in deducts_balance=True should deduct wallet and set paid_at."""
        payload = {
            "title": "Makan Siang",
            "amount": "30000.00",
            "column": self.col_paid.id,
            "wallet": self.wallet.id,
            "category": self.category.id,
        }
        response = self.client.post("/api/expenses/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("70000.00"))

        card = ExpenseCard.objects.get(id=response.data["card"]["id"])
        self.assertIsNotNone(card.paid_at)

    def test_create_expense_paid_insufficient_balance_rejected(self):
        """Creating card with amount > balance directly in paid column fails with 400."""
        payload = {
            "title": "Belanja Mewah",
            "amount": "200000.00",  # Wallet only has 100,000
            "column": self.col_paid.id,
            "wallet": self.wallet.id,
        }
        response = self.client.post("/api/expenses/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        self.assertEqual(ExpenseCard.objects.count(), 0)

    def test_move_card_to_paid_deducts_balance(self):
        """Moving card from False to True column deducts balance and sets paid_at."""
        card = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_unpaid,
            wallet=self.wallet,
            title="Tagihan Listrik",
            amount=Decimal("40000.00"),
            position=100.0,
        )

        response = self.client.patch(
            f"/api/expenses/{card.id}/move/",
            {"target_column_id": self.col_paid.id, "new_position": 500.0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.wallet.refresh_from_db()
        card.refresh_from_db()

        self.assertEqual(self.wallet.balance, Decimal("60000.00"))
        self.assertEqual(card.column_id, self.col_paid.id)
        self.assertEqual(card.position, 500.0)
        self.assertIsNotNone(card.paid_at)

    def test_move_card_insufficient_balance_rejects_and_rolls_back(self):
        """Moving to paid column fails and rolls back atomically if balance is not enough."""
        card = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_unpaid,
            wallet=self.wallet,
            title="Sewa Apartemen",
            amount=Decimal("150000.00"),  # > 100,000
            position=100.0,
        )

        response = self.client.patch(
            f"/api/expenses/{card.id}/move/",
            {"target_column_id": self.col_paid.id, "new_position": 500.0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.wallet.refresh_from_db()
        card.refresh_from_db()

        # Balance remains unchanged
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        # Card remains in unpaid column
        self.assertEqual(card.column_id, self.col_unpaid.id)
        self.assertEqual(card.position, 100.0)
        self.assertIsNone(card.paid_at)

    def test_move_card_from_paid_to_unpaid_refunds_balance(self):
        """Moving card from True to False column refunds wallet balance and clears paid_at."""
        card = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_paid,
            wallet=self.wallet,
            title="Langganan Internet",
            amount=Decimal("40000.00"),
            position=100.0,
            paid_at=timezone.now(),
        )
        # Simulate that balance was already deducted (starts at 60,000)
        self.wallet.balance = Decimal("60000.00")
        self.wallet.save()

        response = self.client.patch(
            f"/api/expenses/{card.id}/move/",
            {"target_column_id": self.col_unpaid.id, "new_position": 250.0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.wallet.refresh_from_db()
        card.refresh_from_db()

        # Balance refunded back to 100,000
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        self.assertEqual(card.column_id, self.col_unpaid.id)
        self.assertEqual(card.position, 250.0)
        self.assertIsNone(card.paid_at)

    def test_delete_card_in_paid_column_refunds_balance(self):
        """Deleting a card from deducts_balance=True column refunds balance."""
        card = ExpenseCard.objects.create(
            user=self.user,
            column=self.col_paid,
            wallet=self.wallet,
            title="Belanja Baju",
            amount=Decimal("35000.00"),
            position=100.0,
            paid_at=timezone.now(),
        )
        self.wallet.balance = Decimal("65000.00")
        self.wallet.save()

        response = self.client.delete(f"/api/expenses/{card.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        self.assertFalse(ExpenseCard.objects.filter(id=card.id).exists())

    def test_transfer_wallet_success(self):
        """Test transferring balance between two wallets atomically."""
        wallet2 = Wallet.objects.create(
            user=self.user, name="Dompet Kedua", balance=Decimal("50000.00")
        )

        response = self.client.post(
            "/api/wallets/transfer/",
            {
                "from_wallet_id": self.wallet.id,
                "to_wallet_id": wallet2.id,
                "amount": "30000.00",
                "notes": "Topup",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.wallet.refresh_from_db()
        wallet2.refresh_from_db()

        self.assertEqual(self.wallet.balance, Decimal("70000.00"))
        self.assertEqual(wallet2.balance, Decimal("80000.00"))

    def test_transfer_wallet_insufficient_balance(self):
        """Test transfer rejected when from_wallet balance is insufficient."""
        wallet2 = Wallet.objects.create(
            user=self.user, name="Dompet Kedua", balance=Decimal("10000.00")
        )

        response = self.client.post(
            "/api/wallets/transfer/",
            {
                "from_wallet_id": self.wallet.id,
                "to_wallet_id": wallet2.id,
                "amount": "200000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.wallet.refresh_from_db()
        wallet2.refresh_from_db()

        self.assertEqual(self.wallet.balance, Decimal("100000.00"))
        self.assertEqual(wallet2.balance, Decimal("10000.00"))

    def test_transfer_same_wallet_rejected(self):
        """Test transfer fails when from_wallet and to_wallet are identical."""
        response = self.client.post(
            "/api/wallets/transfer/",
            {
                "from_wallet_id": self.wallet.id,
                "to_wallet_id": self.wallet.id,
                "amount": "10000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

