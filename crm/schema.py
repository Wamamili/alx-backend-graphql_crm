import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from graphene_django.filter import DjangoFilterConnectionField
from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product
# =====================================
# GraphQL Object Types
# =====================================
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

# =====================================
# Input Types
# =====================================
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

# =====================================
# Mutations
# =====================================

# --- CreateCustomer ---
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        email = input.email
        phone = input.phone
        name = input.name

        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Validate phone format
        if phone and not re.match(r"^\+?\d{3,15}$", phone):
            raise Exception("Invalid phone format. Use +1234567890")

        # Create customer
        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully.")


# --- BulkCreateCustomers ---
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created = []
        errors = []
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"{data.email}: Email already exists")
                    continue

                if data.phone and not re.match(r"^\+?\d{3,15}$", data.phone):
                    errors.append(f"{data.email}: Invalid phone format")
                    continue

                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                created.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


# --- CreateProduct ---
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# --- CreateOrder ---
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        # Validate customer
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        # Validate product IDs
        if not product_ids:
            raise Exception("At least one product must be provided.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more invalid product IDs.")

        # Create order and calculate total
        order = Order.objects.create(
            customer=customer,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        total = sum(p.price for p in products)
        order.total_amount = total
        order.save()

        return CreateOrder(order=order)


# =====================================
# Root Query
# =====================================
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


# =====================================
# Root Mutation
# =====================================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

class CRMQuery(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.String())

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

# This is the requirement for the project checker:
class Query(CRMQuery, graphene.ObjectType):
    pass



class UpdateLowStockProducts(graphene.Mutation):
    message = graphene.String()
    updated_products = graphene.List(graphene.String)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_names = []

        for product in low_stock_products:
            product.stock += 10  # simulate restocking
            product.save()
            updated_names.append(f"{product.name}: {product.stock}")

        msg = "Low stock products updated successfully." if updated_names else "No low stock products found."
        return UpdateLowStockProducts(message=msg, updated_products=updated_names)

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# ✅ Ensure Query class is already present
class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
