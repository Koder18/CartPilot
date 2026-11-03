from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.store.models import Category, Product, PriceSnapshot

class Command(BaseCommand):
    help = "Create sample categories and products for local development."

    def handle(self, *args, **options):
        samples = {
            "Desk & Tech": [
                # Desk & Tech
                ("Wireless Headphones", "Comfortable wireless headphones for everyday listening.", "2499.00", 18, "audio,wireless,tech", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"),
                ("Mechanical Keyboard", "A compact keyboard for focused work and gaming.", "3299.00", 12, "keyboard,desk,tech", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600"),
                ("Laptop Stand", "An adjustable stand to make a desk setup more comfortable.", "899.00", 25, "desk,ergonomic,accessory", "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600"),
            ],
            "Everyday Carry": [
                ("Insulated Bottle", "Reusable bottle for commutes, work, and travel.", "599.00", 40, "bottle,travel,reusable", ""),
                ("Canvas Tote", "A durable tote for daily errands and shopping.", "399.00", 32, "bag,reusable,accessory", ""),
                ("Compact Umbrella", "A lightweight umbrella for unpredictable weather.", "749.00", 16, "travel,weather,accessory", ""),
            ],
            "Home Comfort": [
                ("Desk Lamp", "A warm, adjustable lamp for reading and work.", "1199.00", 14, "home,lighting,desk", ""),
                ("Ceramic Mug", "A simple ceramic mug for your everyday coffee or tea.", "349.00", 50, "home,kitchen,mug", ""),
                ("Soft Throw", "A comfortable throw for relaxing at home.", "1599.00", 9, "home,comfort", ""),
            ],
        }
        for category_name, products in samples.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={"description": f"Curated {category_name.lower()} products."})
            for name, description, price, stock, tags, image_url in products:
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": category, "description": description,
                        "price": Decimal(price), "stock": stock, "tags": tags,
                        "image_url": image_url, "is_active": True,
                    },
                )
                if created:
                    PriceSnapshot.objects.create(product=product, price=product.price)

                if image_url and product.image_url != image_url:
                    product.image_url = image_url
                    product.save(update_fields=["image_url"])
        self.stdout.write(self.style.SUCCESS("Demo catalog created or already present."))
