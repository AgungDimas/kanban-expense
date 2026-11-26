from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BoardView,
    WalletViewSet,
    CategoryViewSet,
    ExpenseCardViewSet,
    AnalyticsSummaryView,
    ExportCSVView,
)

router = DefaultRouter()
router.register(r"wallets", WalletViewSet, basename="wallet")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"expenses", ExpenseCardViewSet, basename="expense")

urlpatterns = [
    path("board/", BoardView.as_view(), name="board"),
    path("analytics/summary/", AnalyticsSummaryView.as_view(), name="analytics-summary"),
    path("export/", ExportCSVView.as_view(), name="export-csv"),
    path("", include(router.urls)),
]
