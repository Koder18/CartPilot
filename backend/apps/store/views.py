from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Count, F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    Category, Product, CartItem, WishlistItem, Address, ShoppingPlan,
    ShoppingPlanItem, Order, OrderItem, Review, Budget, PriceAlert, PriceSnapshot
)
from .serializers import (
    RegisterSerializer, UserSerializer, CategorySerializer, ProductSerializer,
    CartItemSerializer, WishlistItemSerializer, AddressSerializer,
    ShoppingPlanSerializer, ShoppingPlanItemSerializer, OrderSerializer,
    ReviewSerializer, BudgetSerializer, PriceAlertSerializer, PriceSnapshotSerializer
)
from .permissions import IsStaffOrReadOnly

User = get_user_model()

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok", "message": "CartPilot API is running.", "version": "v1"})

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = "id"

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    def get_queryset(self):
        qs = Product.objects.select_related("category").filter(is_active=True)
        params = self.request.query_params
        category = params.get("category")
        search = params.get("search")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        ordering = params.get("ordering", "-created_at")
        if category:
            qs = qs.filter(category_id=category)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search) | Q(tags__icontains=search))
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if ordering in {"price", "-price", "name", "-name", "created_at", "-created_at"}:
            qs = qs.order_by(ordering)
        return qs

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        items = CartItem.objects.filter(user=request.user).select_related("product", "product__category")
        subtotal = sum((item.product.price * item.quantity for item in items), Decimal("0.00"))
        return Response({"items": CartItemSerializer(items, many=True).data, "subtotal": subtotal, "item_count": sum(i.quantity for i in items)})
    def post(self, request):
        product = get_object_or_404(Product, pk=request.data.get("product"), is_active=True)
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"detail": "Quantity must be a positive integer."}, status=400)
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)
        if quantity > product.stock:
            return Response({"detail": "Requested quantity exceeds available stock."}, status=400)
        item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={"quantity": quantity})
        if not created:
            if item.quantity + quantity > product.stock:
                return Response({"detail": "Requested quantity exceeds available stock."}, status=400)
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, user=request.user)
        try:
            quantity = int(request.data.get("quantity"))
        except (TypeError, ValueError):
            return Response({"detail": "Quantity must be a positive integer."}, status=400)
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)
        if quantity > item.product.stock:
            return Response({"detail": "Requested quantity exceeds available stock."}, status=400)
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])
        return Response(CartItemSerializer(item).data)
    def delete(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, user=request.user)
        item.delete()
        return Response(status=204)

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        items = WishlistItem.objects.filter(user=request.user).select_related("product", "product__category")
        return Response(WishlistItemSerializer(items, many=True).data)
    def post(self, request):
        product = get_object_or_404(Product, pk=request.data.get("product"), is_active=True)
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response(WishlistItemSerializer(item).data, status=201 if created else 200)

class WishlistItemDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        item = get_object_or_404(WishlistItem, pk=pk, user=request.user)
        item.delete()
        return Response(status=204)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class ShoppingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingPlanSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ShoppingPlan.objects.filter(user=self.request.user).prefetch_related("items__product")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PlanItemView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, plan_id):
        plan = get_object_or_404(ShoppingPlan, pk=plan_id, user=request.user)
        product = get_object_or_404(Product, pk=request.data.get("product"), is_active=True)
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"detail": "Quantity must be a positive integer."}, status=400)
        if quantity < 1:
            return Response({"detail": "Quantity must be at least 1."}, status=400)
        target_price = request.data.get("target_price")
        item, created = ShoppingPlanItem.objects.update_or_create(
            plan=plan, product=product,
            defaults={"quantity": quantity, "target_price": target_price or None},
        )
        return Response(ShoppingPlanItemSerializer(item).data, status=201 if created else 200)
    def delete(self, request, plan_id, item_id):
        item = get_object_or_404(ShoppingPlanItem, pk=item_id, plan__id=plan_id, plan__user=request.user)
        item.delete()
        return Response(status=204)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        cart_items = list(CartItem.objects.select_for_update().filter(user=request.user).select_related("product"))
        if not cart_items:
            return Response({"detail": "Your cart is empty."}, status=400)
        shipping_name = str(request.data.get("shipping_name", "")).strip()
        shipping_phone = str(request.data.get("shipping_phone", "")).strip()
        shipping_address = str(request.data.get("shipping_address", "")).strip()
        payment_method = request.data.get("payment_method", "demo")
        if not all([shipping_name, shipping_phone, shipping_address]):
            return Response({"detail": "Shipping name, phone, and address are required."}, status=400)
        if payment_method not in {"demo", "cod"}:
            return Response({"detail": "Unsupported payment method. Use demo or cod."}, status=400)
        # Lock product rows and validate stock/price on the server.
        product_ids = [item.product_id for item in cart_items]
        products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids, is_active=True)}
        if len(products) != len(product_ids):
            return Response({"detail": "One or more products are no longer available."}, status=400)
        subtotal = Decimal("0.00")
        for item in cart_items:
            product = products[item.product_id]
            if item.quantity > product.stock:
                return Response({"detail": f"Not enough stock for {product.name}. Available: {product.stock}."}, status=400)
            subtotal += product.price * item.quantity
        shipping_fee = Decimal("0.00") if subtotal >= Decimal("1000.00") else Decimal("49.00")
        order = Order.objects.create(
            user=request.user, status="confirmed", payment_method=payment_method,
            payment_status="unpaid" if payment_method == "cod" else "demo",
            subtotal=subtotal, shipping_fee=shipping_fee, total=subtotal + shipping_fee,
            shipping_name=shipping_name, shipping_phone=shipping_phone, shipping_address=shipping_address,
        )
        for item in cart_items:
            product = products[item.product_id]
            OrderItem.objects.create(
                order=order, product=product, product_name=product.name,
                unit_price=product.price, quantity=item.quantity,
                line_total=product.price * item.quantity,
            )
            product.stock -= item.quantity
            product.save(update_fields=["stock", "updated_at"])
            PriceSnapshot.objects.create(product=product, price=product.price)
            for alert in PriceAlert.objects.filter(product=product, is_active=True, target_price__gte=product.price):
                alert.is_active = False
                alert.triggered_at = timezone.now()
                alert.save(update_fields=["is_active", "triggered_at", "updated_at"])
        CartItem.objects.filter(user=request.user).delete()
        return Response(OrderSerializer(order).data, status=201)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items").order_by("-created_at")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update().prefetch_related("items"), pk=pk, user=request.user)
            if order.status not in {"pending", "confirmed"}:
                return Response({"detail": "Only pending or confirmed orders can be cancelled."}, status=400)
            for item in order.items.all():
                product = Product.objects.select_for_update().filter(pk=item.product_id).first()
                if product:
                    product.stock += item.quantity
                    product.save(update_fields=["stock", "updated_at"])
            order.status = "cancelled"
            order.cancelled_at = timezone.now()
            order.save(update_fields=["status", "cancelled_at", "updated_at"])
        return Response(OrderSerializer(order).data)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = Review.objects.select_related("user", "product")
        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user.id and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own reviews.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if self.action == "list":
            for budget in serializer.instance or []:
                budget.spent = self._spent_for_month(budget.month)
        elif self.action == "retrieve" and serializer.instance:
            serializer.instance.spent = self._spent_for_month(serializer.instance.month)
        return serializer
    def _spent_for_month(self, month):
        start = month.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        result = Order.objects.filter(user=self.request.user, status__in=["confirmed", "shipped", "delivered"], created_at__date__gte=start, created_at__date__lt=end).aggregate(total=Sum("total"))["total"]
        return result or Decimal("0.00")
    def perform_create(self, serializer):
        month = serializer.validated_data["month"]
        if month.day != 1:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"month": "Use the first day of the month, e.g. 2026-10-01."})
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        month = serializer.validated_data.get("month", serializer.instance.month)
        if month.day != 1:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"month": "Use the first day of the month, e.g. 2026-10-01."})
        serializer.save(user=self.request.user)

class PriceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = PriceAlertSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user).select_related("product", "product__category")
    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        alert, created = PriceAlert.objects.get_or_create(
            user=self.request.user, product=product,
            defaults={"target_price": serializer.validated_data["target_price"], "is_active": True},
        )
        if not created:
            alert.target_price = serializer.validated_data["target_price"]
            alert.is_active = True
            alert.triggered_at = None
            alert.save()
            serializer.instance = alert
        else:
            serializer.instance = alert

class RecommendationView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = Product.objects.filter(is_active=True, stock__gt=0).select_related("category")
        category_id = request.query_params.get("category")
        budget = request.query_params.get("budget")
        reason = "Popular available products"
        if request.user.is_authenticated:
            purchased_ids = OrderItem.objects.filter(order__user=request.user).values_list("product_id", flat=True)
            categories = OrderItem.objects.filter(order__user=request.user).values_list("product__category_id", flat=True)
            if categories.exists():
                products = products.filter(category_id=categories.first())
                reason = "Based on a category from your order history"
            elif purchased_ids.exists():
                products = products.exclude(id__in=purchased_ids)
                reason = "Discover something new"
        if category_id:
            products = products.filter(category_id=category_id)
            reason = "Matches your selected category"
        if budget:
            try:
                products = products.filter(price__lte=Decimal(budget))
                reason = f"Within your budget of {budget}"
            except Exception:
                return Response({"detail": "budget must be a valid number."}, status=400)
        data = ProductSerializer(products.order_by("-created_at")[:8], many=True).data
        return Response({"reason": reason, "results": data})

class InsightsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        now = timezone.localdate()
        start = now.replace(day=1)
        orders = Order.objects.filter(user=request.user, status__in=["confirmed", "shipped", "delivered"])
        month_orders = orders.filter(created_at__date__gte=start)
        spent = month_orders.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
        budget = Budget.objects.filter(user=request.user, month=start).first()
        by_category = OrderItem.objects.filter(order__in=month_orders).values(category_name=F("product__category__name")).annotate(total=Sum("line_total")).order_by("-total")
        best_sellers = OrderItem.objects.values("product_name").annotate(quantity_sold=Sum("quantity"), revenue=Sum("line_total")).order_by("-quantity_sold")[:5] if request.user.is_staff else []
        return Response({
            "month": start,
            "spent_this_month": spent,
            "budget": budget.amount if budget else None,
            "budget_remaining": (budget.amount - spent) if budget else None,
            "orders_this_month": month_orders.count(),
            "total_orders": orders.count(),
            "spending_by_category": list(by_category),
            "recent_orders": OrderSerializer(orders.order_by("-created_at")[:5], many=True).data,
            "best_sellers": list(best_sellers),
        })

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        paidish = Order.objects.filter(status__in=["confirmed", "shipped", "delivered"])
        return Response({
            "total_products": Product.objects.count(),
            "active_products": Product.objects.filter(is_active=True).count(),
            "total_customers": User.objects.filter(is_staff=False).count(),
            "total_orders": Order.objects.count(),
            "revenue": paidish.aggregate(total=Sum("total"))["total"] or Decimal("0.00"),
            "orders_by_status": list(Order.objects.values("status").annotate(count=Count("id")).order_by("status")),
            "low_stock_products": ProductSerializer(Product.objects.filter(stock__lte=5, is_active=True).select_related("category")[:10], many=True).data,
            "best_sellers": list(OrderItem.objects.values("product_name").annotate(quantity_sold=Sum("quantity"), revenue=Sum("line_total")).order_by("-quantity_sold")[:5]),
        })

class PriceHistoryView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        snapshots = PriceSnapshot.objects.filter(product=product)
        return Response({"product_id": product.id, "current_price": product.price, "history": PriceSnapshotSerializer(snapshots, many=True).data})
