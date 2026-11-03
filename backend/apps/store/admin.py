from django.contrib import admin
from .models import (
    Category, Product, CartItem, WishlistItem, Address, ShoppingPlan,
    ShoppingPlanItem, Order, OrderItem, Review, Budget, PriceAlert, PriceSnapshot
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description", "tags")
    prepopulated_fields = {"slug": ("name",)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("user__username", "shipping_name", "shipping_phone")
    inlines = [OrderItemInline]

admin.site.register([CartItem, WishlistItem, Address, ShoppingPlan, ShoppingPlanItem, Review, Budget, PriceAlert, PriceSnapshot])
