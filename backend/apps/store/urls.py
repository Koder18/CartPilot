from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    health_check, RegisterView, MeView, CategoryViewSet, ProductViewSet,
    CartView, CartItemDetailView, WishlistView, WishlistItemDetailView,
    AddressViewSet, ShoppingPlanViewSet, PlanItemView, CheckoutView,
    OrderViewSet, ReviewViewSet, BudgetViewSet, PriceAlertViewSet,
    RecommendationView, InsightsView, AdminAnalyticsView, PriceHistoryView
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("addresses", AddressViewSet, basename="address")
router.register("shopping-plans", ShoppingPlanViewSet, basename="shopping-plan")
router.register("orders", OrderViewSet, basename="order")
router.register("reviews", ReviewViewSet, basename="review")
router.register("budgets", BudgetViewSet, basename="budget")
router.register("price-alerts", PriceAlertViewSet, basename="price-alert")

urlpatterns = [
    path("health/", health_check),
    path("auth/register/", RegisterView.as_view()),
    path("auth/token/", TokenObtainPairView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("cart/", CartView.as_view()),
    path("cart/items/<int:pk>/", CartItemDetailView.as_view()),
    path("wishlist/", WishlistView.as_view()),
    path("wishlist/<int:pk>/", WishlistItemDetailView.as_view()),
    path("shopping-plans/<int:plan_id>/items/", PlanItemView.as_view()),
    path("shopping-plans/<int:plan_id>/items/<int:item_id>/", PlanItemView.as_view()),
    path("checkout/", CheckoutView.as_view()),
    path("recommendations/", RecommendationView.as_view()),
    path("insights/summary/", InsightsView.as_view()),
    path("admin/analytics/", AdminAnalyticsView.as_view()),
    path("products/<int:product_id>/price-history/", PriceHistoryView.as_view()),
    path("", include(router.urls)),
]
