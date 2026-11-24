from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardView,
    WalletViewSet,
    CategoryViewSet,
    ExpenseCardViewSet,
)

router = DefaultRouter()
router.register(r"wallets", WalletViewSet, basename="wallet")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"expenses", ExpenseCardViewSet, basename="expense")

urlpatterns = [
    path("board/", BoardView.as_view(), name="board"),
    path("", include(router.urls)),
]
