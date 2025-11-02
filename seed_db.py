import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

def seed():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
    ]
    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Phone", "price": 499.99, "stock": 15},
    ]
    for c in customers:
        Customer.objects.get_or_create(email=c["email"], defaults=c)
    for p in products:
        Product.objects.get_or_create(name=p["name"], defaults=p)
    print("✅ Database seeded successfully.")

if __name__ == "__main__":
    seed()
