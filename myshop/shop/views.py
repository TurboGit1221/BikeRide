#Imports
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status

from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer
from .forms import ContactForm, RegisterForm, CustomUserCreationForm


# ================== API Views ==================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return []
        return [IsAdminUser()]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get('product_id')
    try:
        quantity = int(request.data.get('quantity', 1))
    except (TypeError, ValueError):
        return Response(
            {"message": "Ilość musi być liczbą całkowitą"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity < 1:
        return Response(
            {"message": "Ilość musi być większa od zera"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart, _ = Cart.objects.get_or_create(user=user)
    product = get_object_or_404(Product, id=product_id)

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    new_quantity = quantity if cart_item is None else cart_item.quantity + quantity

    if new_quantity > product.stock:
        return Response(
            {"message": "Brak wystarczającej liczby produktów w magazynie"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    CartItem.objects.update_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': new_quantity},
    )

    return Response({"message": "Produkt dodany do koszyka"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_order(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    if cart.items.count() == 0:
        return Response({"message": "Koszyk jest pusty"}, status=400)

    cart_items = list(
        cart.items.select_related('product').select_for_update()
    )

    for item in cart_items:
        if item.quantity > item.product.stock:
            return Response(
                {"message": f"Brak produktu: {item.product.name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    order = Order.objects.create(user=user, total_price=total_price)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        item.product.stock -= item.quantity
        item.product.save(update_fields=['stock'])

    cart.items.all().delete()  # Czyścimy koszyk

    return Response(
        {"message": "Zamówienie utworzone!", "order_id": order.id},
        status=status.HTTP_201_CREATED,
    )


# ================== Frontend Views ==================

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})


@login_required
def cart_view(request):
    return render(request, 'cart.html')


def contact_view(request):
    sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            sent = True
            form = ContactForm()
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, 'sent': sent})


# ================== Auth Views ==================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Nieprawidłowe dane logowania'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
