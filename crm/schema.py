import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order

# ==========================
# GraphQL Object Types
# ==========================
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# ==========================
# Queries
# ==========================
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()

# ==========================
# Mutations
# ==========================

# ---- CreateCustomer ----
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone and not re.match(r"^\+?\d{3,15}$", phone):
            raise Exception("Invalid phone format")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


# ---- BulkCreateCustomers ----
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(
                graphene.InputObjectType(
                    name="CustomerInput",
                    fields={
                        "name": graphene.String(),
                        "email": graphene.String(),
                        "phone": graphene.String(),
                    },
                )
            )
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []
        for data in input:
            try:
                if Customer.objects.filter(email=data["email"]).exists():
                    errors.append(f"{data['email']} already exists")
                    continue
                if data.get("phone") and not re.match(r"^\+?\d{3,15}$", data["phone"]):
                    errors.append(f"Invalid phone for {data['email']}")
                    continue
                c = Customer.objects.create(
                    name=data["name"], email=data["email"], phone=data.get("phone")
                )
                created_customers.append(c)
            except Exception as e:
                errors.append(str(e))
        return BulkCreateCustomers(customers=created_customers, errors=errors)


# ---- CreateProduct ----
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# ---- CreateOrder ----
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more invalid product IDs")

        order = Order.objects.create(
            customer=customer, order_date=order_date or timezone.now()
        )
        order.products.set(products)
        order.calculate_total()
        return CreateOrder(order=order)


# ==========================
# Root Mutation Class
# ==========================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
