from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets", null=True, blank=True)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} (Rp {self.balance:,.2f})"


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)
    name = models.CharField(max_length=100)
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    color = models.CharField(max_length=7, default="#3B82F6")  # Hex color string e.g. #EF4444
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["id"]

    def __str__(self):
        return self.name


class BoardColumn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="board_columns", null=True, blank=True)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    deducts_balance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} (order: {self.order}, deducts: {self.deducts_balance})"


class ExpenseCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses", null=True, blank=True)
    column = models.ForeignKey(BoardColumn, on_delete=models.CASCADE, related_name="cards")
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="cards")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="cards")
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True, default="")
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    position = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.title} - Rp {self.amount:,.2f}"
