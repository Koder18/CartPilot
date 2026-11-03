from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from .models import (
    Category, Product, CartItem, WishlistItem, Address, ShoppingPlan,
    ShoppingPlanItem, Order, OrderItem, Review, Budget, PriceAlert, PriceSnapshot
)
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "first_name", "last_name"]
    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs
    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username", "email"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "category", "category_name", "name", "slug", "description", "price", "image_url", "stock", "is_active", "tags", "average_rating", "review_count", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
    def get_average_rating(self, obj):
        value = obj.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(value, 1) if value is not None else None
    def get_review_count(self, obj):
        return obj.reviews.count()

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = CartItem
        fields = ["id", "product", "product_detail", "quantity", "line_total", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class WishlistItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_detail", "created_at"]
        read_only_fields = ["id", "created_at"]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "full_name", "phone", "line1", "line2", "city", "state", "postal_code", "country", "is_default", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class ShoppingPlanItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    class Meta:
        model = ShoppingPlanItem
        fields = ["id", "product", "product_detail", "target_price", "quantity", "created_at"]
        read_only_fields = ["id", "created_at"]

class ShoppingPlanSerializer(serializers.ModelSerializer):
    items = ShoppingPlanItemSerializer(many=True, read_only=True)
    class Meta:
        model = ShoppingPlan
        fields = ["id", "name", "monthly_budget", "target_date", "items", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "unit_price", "quantity", "line_total"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "status", "payment_method", "payment_status", "subtotal", "shipping_fee", "total", "shipping_name", "shipping_phone", "shipping_address", "items", "created_at", "updated_at", "cancelled_at"]
        read_only_fields = fields

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Review
        fields = ["id", "product", "user", "username", "rating", "title", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "username", "created_at", "updated_at"]

class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, required=False)
    class Meta:
        model = Budget
        fields = ["id", "month", "amount", "spent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class PriceSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceSnapshot
        fields = ["id", "price", "created_at"]
        read_only_fields = fields

class PriceAlertSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    current_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = PriceAlert
        fields = ["id", "product", "product_detail", "target_price", "current_price", "is_active", "triggered_at", "created_at", "updated_at"]
        read_only_fields = ["id", "triggered_at", "created_at", "updated_at"]
