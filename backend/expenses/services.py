from decimal import Decimal
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from .models import ExpenseCard, BoardColumn, Wallet

User = get_user_model()


def get_default_user():
    """Retrieve demo or first available user for MVP."""
    user = User.objects.filter(username="demo").first()
    if not user:
        user = User.objects.first()
    if not user:
        user = User.objects.create_user(
            username="demo",
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
        )
    return user


def move_card(card_id: int, target_column_id: int, new_position: float) -> tuple[ExpenseCard, Wallet]:
    """
    Move card to a new column and position with atomic balance update and locking.
    
    Business Rules:
    - Moving from deducts_balance=False to True:
      Deduct wallet balance. If insufficient, reject with HTTP 400 (ValidationError).
      Set paid_at to timezone.now().
    - Moving from deducts_balance=True to False:
      Refund wallet balance. Clear paid_at to None.
    - Moving within same deducts_balance type:
      No balance changes.
    - Uses transaction.atomic() and select_for_update() on both card and wallet.
    """
    with transaction.atomic():
        try:
            card = (
                ExpenseCard.objects.select_for_update()
                .select_related("column", "wallet")
                .get(id=card_id)
            )
        except ExpenseCard.DoesNotExist:
            raise ValidationError({"detail": f"Kartu dengan ID {card_id} tidak ditemukan."})

        try:
            target_column = BoardColumn.objects.get(id=target_column_id)
        except BoardColumn.DoesNotExist:
            raise ValidationError({"detail": f"Kolom tujuan dengan ID {target_column_id} tidak ditemukan."})

        current_column = card.column
        wallet = Wallet.objects.select_for_update().get(id=card.wallet_id)

        # Transition 1: False -> True (Potong Saldo)
        if not current_column.deducts_balance and target_column.deducts_balance:
            if wallet.balance < card.amount:
                raise ValidationError({
                    "balance": (
                        f"Saldo tidak mencukupi di dompet '{wallet.name}'. "
                        f"Sisa saldo: Rp {wallet.balance:,.2f}, dibutuhkan: Rp {card.amount:,.2f}."
                    )
                })
            wallet.balance -= card.amount
            wallet.save(update_fields=["balance"])
            card.paid_at = timezone.now()

        # Transition 2: True -> False (Rollback / Refund Saldo)
        elif current_column.deducts_balance and not target_column.deducts_balance:
            wallet.balance += card.amount
            wallet.save(update_fields=["balance"])
            card.paid_at = None

        # Transition 3: True -> True (Tetap lunas, pastikan paid_at terisi)
        elif current_column.deducts_balance and target_column.deducts_balance:
            if not card.paid_at:
                card.paid_at = timezone.now()

        # Update card column and position
        card.column = target_column
        card.position = float(new_position)
        card.save(update_fields=["column", "position", "paid_at"])

        return card, wallet


def create_card(validated_data: dict, user=None) -> ExpenseCard:
    """
    Create a new expense card.
    If placed directly into a column where deducts_balance=True,
    atomically deduct the wallet balance or reject if insufficient funds.
    """
    if not user:
        user = get_default_user()
    validated_data["user"] = user

    column = validated_data["column"]
    wallet = validated_data["wallet"]
    amount = validated_data["amount"]

    # Compute default position if not provided
    if "position" not in validated_data or validated_data["position"] is None or validated_data["position"] == 0:
        max_pos = ExpenseCard.objects.filter(column=column).aggregate(max_pos=Max("position"))["max_pos"]
        validated_data["position"] = (max_pos or 0.0) + 1000.0

    with transaction.atomic():
        if column.deducts_balance:
            locked_wallet = Wallet.objects.select_for_update().get(id=wallet.id)
            if locked_wallet.balance < amount:
                raise ValidationError({
                    "balance": (
                        f"Saldo tidak mencukupi di dompet '{locked_wallet.name}'. "
                        f"Sisa saldo: Rp {locked_wallet.balance:,.2f}, dibutuhkan: Rp {amount:,.2f}."
                    )
                })
            locked_wallet.balance -= amount
            locked_wallet.save(update_fields=["balance"])
            validated_data["paid_at"] = timezone.now()
        else:
            validated_data["paid_at"] = None

        card = ExpenseCard.objects.create(**validated_data)
        return card


def delete_card(card_id: int) -> Wallet | None:
    """
    Delete an expense card.
    If the card is currently in a column where deducts_balance=True,
    atomically refund the amount back to its wallet.
    """
    with transaction.atomic():
        try:
            card = (
                ExpenseCard.objects.select_for_update()
                .select_related("column", "wallet")
                .get(id=card_id)
            )
        except ExpenseCard.DoesNotExist:
            raise ValidationError({"detail": f"Kartu dengan ID {card_id} tidak ditemukan."})

        wallet = None
        if card.column.deducts_balance:
            wallet = Wallet.objects.select_for_update().get(id=card.wallet_id)
            wallet.balance += card.amount
            wallet.save(update_fields=["balance"])

        card.delete()
        return wallet


def update_card(card_id: int, validated_data: dict) -> ExpenseCard:
    """
    Update an expense card safely with atomic balance reconciliation
    if amount or wallet changes while in a deducts_balance=True column.
    """
    with transaction.atomic():
        card = (
            ExpenseCard.objects.select_for_update()
            .select_related("column", "wallet")
            .get(id=card_id)
        )

        old_wallet = card.wallet
        old_amount = card.amount
        is_paid = card.column.deducts_balance

        new_wallet = validated_data.get("wallet", old_wallet)
        new_amount = validated_data.get("amount", old_amount)

        if is_paid:
            if old_wallet.id == new_wallet.id:
                # Same wallet, adjust difference
                diff = new_amount - old_amount
                if diff != 0:
                    locked_wallet = Wallet.objects.select_for_update().get(id=old_wallet.id)
                    if diff > 0 and locked_wallet.balance < diff:
                        raise ValidationError({
                            "balance": f"Saldo tidak mencukupi untuk penambahan nominal pada '{locked_wallet.name}'."
                        })
                    locked_wallet.balance -= diff
                    locked_wallet.save(update_fields=["balance"])
            else:
                # Changed wallet: refund old wallet, deduct new wallet
                locked_old_wallet = Wallet.objects.select_for_update().get(id=old_wallet.id)
                locked_old_wallet.balance += old_amount
                locked_old_wallet.save(update_fields=["balance"])

                locked_new_wallet = Wallet.objects.select_for_update().get(id=new_wallet.id)
                if locked_new_wallet.balance < new_amount:
                    raise ValidationError({
                        "balance": f"Saldo tidak mencukupi di dompet baru '{locked_new_wallet.name}'."
                    })
                locked_new_wallet.balance -= new_amount
                locked_new_wallet.save(update_fields=["balance"])

        for key, value in validated_data.items():
            setattr(card, key, value)
        card.save()
        return card


def transfer_wallet_balance(from_wallet_id: int, to_wallet_id: int, amount: Decimal, notes: str = "") -> tuple[Wallet, Wallet]:
    """
    Transfer balance between two wallets atomically with select_for_update().
    """
    if from_wallet_id == to_wallet_id:
        raise ValidationError({"detail": "Dompet asal dan dompet tujuan tidak boleh sama."})

    if amount <= Decimal("0.00"):
        raise ValidationError({"amount": "Nominal transfer harus lebih besar dari Rp 0."})

    with transaction.atomic():
        try:
            from_wallet = Wallet.objects.select_for_update().get(id=from_wallet_id)
        except Wallet.DoesNotExist:
            raise ValidationError({"from_wallet_id": "Dompet asal tidak ditemukan."})

        try:
            to_wallet = Wallet.objects.select_for_update().get(id=to_wallet_id)
        except Wallet.DoesNotExist:
            raise ValidationError({"to_wallet_id": "Dompet tujuan tidak ditemukan."})

        if from_wallet.balance < amount:
            raise ValidationError({
                "balance": (
                    f"Saldo pada dompet '{from_wallet.name}' tidak mencukupi. "
                    f"Sisa saldo: Rp {from_wallet.balance:,.2f}, dibutuhkan: Rp {amount:,.2f}."
                )
            })

        from_wallet.balance -= amount
        to_wallet.balance += amount
        from_wallet.save(update_fields=["balance"])
        to_wallet.save(update_fields=["balance"])

        return from_wallet, to_wallet

