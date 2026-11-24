from django.contrib import admin
from .models import Wallet, Category, BoardColumn, ExpenseCard


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("name", "balance", "user", "created_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_budget", "color", "user", "created_at")
    search_fields = ("name",)


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "deducts_balance", "user")
    list_editable = ("order", "deducts_balance")


@admin.register(ExpenseCard)
class ExpenseCardAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "column", "wallet", "category", "due_date", "paid_at", "position")
    list_filter = ("column", "wallet", "category")
    search_fields = ("title", "notes")
