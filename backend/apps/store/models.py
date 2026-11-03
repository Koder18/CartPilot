from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    image_url = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags")
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "product"
            slug = base
            counter = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class CartItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_cart_product")]
    @property
    def line_total(self):
        return self.product.price * self.quantity

class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_wishlist_product")]

class Address(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=25)
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=80, default="India")
    is_default = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.full_name} — {self.city}"

class ShoppingPlan(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopping_plans")
    name = models.CharField(max_length=120)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    target_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.name

class ShoppingPlanItem(TimeStampedModel):
    plan = models.ForeignKey(ShoppingPlan, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="planned_items")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0.00"))])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["plan", "product"], name="unique_plan_product")]

class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"), ("confirmed", "Confirmed"), ("shipped", "Shipped"),
        ("delivered", "Delivered"), ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [("cod", "Cash on delivery"), ("demo", "Demo payment")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="demo")
    payment_status = models.CharField(max_length=20, default="unpaid")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_name = models.CharField(max_length=120)
    shipping_phone = models.CharField(max_length=25)
    shipping_address = models.TextField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Order #{self.pk} — {self.user}"

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class Review(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_review")]

class Budget(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    month = models.DateField(help_text="Use the first day of the month")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "month"], name="unique_user_budget_month")]
        ordering = ["-month"]

class PriceSnapshot(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_snapshots")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        ordering = ["created_at"]

class PriceAlert(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="price_alerts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_alerts")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_price_alert")]
