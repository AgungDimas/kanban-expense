import os
import django
from decimal import Decimal

# Setup Django environment if run as standalone script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from expenses.models import BoardColumn, Wallet, Category, ExpenseCard

User = get_user_model()


def run_seed(stdout_write=print):
    stdout_write("Seeding initial data...")

    # 1. Default User
    user, created = User.objects.get_or_create(
        username="demo",
        defaults={
            "email": "demo@example.com",
            "first_name": "Demo",
            "last_name": "User",
        },
    )
    if created:
        user.set_password("demo12345")
        user.save()
        stdout_write(f"[+] Created default user: {user.username}")
    else:
        stdout_write(f"[*] Found existing user: {user.username}")

    # 2. 3 Kolom Default
    columns_data = [
        {"name": "Wishlist / Rencana", "order": 1, "deducts_balance": False},
        {"name": "Tagihan / Belum Bayar", "order": 2, "deducts_balance": False},
        {"name": "Lunas / Paid", "order": 3, "deducts_balance": True},
    ]

    columns = {}
    for col_data in columns_data:
        col, _ = BoardColumn.objects.update_or_create(
            user=user,
            name=col_data["name"],
            defaults={
                "order": col_data["order"],
                "deducts_balance": col_data["deducts_balance"],
            },
        )
        columns[col.name] = col
        stdout_write(f"[+] Column: {col.name} (deducts_balance={col.deducts_balance})")

    # 3. 2 Dompet Dummy
    wallets_data = [
        {"name": "Rekening Utama (BCA)", "balance": Decimal("10000000.00")},
        {"name": "E-Wallet (GoPay/OVO)", "balance": Decimal("1500000.00")},
    ]

    wallets = {}
    for w_data in wallets_data:
        wallet, _ = Wallet.objects.update_or_create(
            user=user,
            name=w_data["name"],
            defaults={"balance": w_data["balance"]},
        )
        wallets[wallet.name] = wallet
        stdout_write(f"[+] Wallet: {wallet.name} - Rp {wallet.balance:,.2f}")

    # 4. 3 Kategori Dummy
    categories_data = [
        {"name": "Makanan & Minuman", "monthly_budget": Decimal("3000000.00"), "color": "#EF4444"},
        {"name": "Tagihan & Utilitas", "monthly_budget": Decimal("2000000.00"), "color": "#3B82F6"},
        {"name": "Hiburan & Belanja", "monthly_budget": Decimal("1500000.00"), "color": "#10B981"},
    ]

    categories = {}
    for cat_data in categories_data:
        cat, _ = Category.objects.update_or_create(
            user=user,
            name=cat_data["name"],
            defaults={
                "monthly_budget": cat_data["monthly_budget"],
                "color": cat_data["color"],
            },
        )
        categories[cat.name] = cat
        stdout_write(f"[+] Category: {cat.name} ({cat.color})")

    # 5. Contoh Kartu Dummy untuk visualisasi awal
    sample_cards = [
        {
            "title": "Beli Headphone Wireless",
            "amount": Decimal("850000.00"),
            "column": columns["Wishlist / Rencana"],
            "wallet": wallets["Rekening Utama (BCA)"],
            "category": categories["Hiburan & Belanja"],
            "notes": "Rencana beli saat promo tanggal kembar",
            "position": 1000.0,
            "paid_at": None,
        },
        {
            "title": "Tagihan Listrik PLN",
            "amount": Decimal("350000.00"),
            "column": columns["Tagihan / Belum Bayar"],
            "wallet": wallets["Rekening Utama (BCA)"],
            "category": categories["Tagihan & Utilitas"],
            "notes": "Jatuh tempo akhir bulan",
            "position": 1000.0,
            "paid_at": None,
        },
        {
            "title": "Makan Siang Tim",
            "amount": Decimal("125000.00"),
            "column": columns["Lunas / Paid"],
            "wallet": wallets["E-Wallet (GoPay/OVO)"],
            "category": categories["Makanan & Minuman"],
            "notes": "Traktir makan siang kantor",
            "position": 1000.0,
            "paid_at": timezone.now(),
        },
    ]

    for card_data in sample_cards:
        card, _ = ExpenseCard.objects.update_or_create(
            user=user,
            title=card_data["title"],
            defaults=card_data,
        )
        stdout_write(f"[+] Card: '{card.title}' in [{card.column.name}]")

    stdout_write("\n[SUCCESS] Seed data completed successfully!")


class Command(BaseCommand):
    help = "Seed database with initial columns, wallets, categories, and sample cards"

    def handle(self, *args, **options):
        run_seed(self.stdout.write)


if __name__ == "__main__":
    run_seed()
