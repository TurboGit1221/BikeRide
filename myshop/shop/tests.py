from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Cart, CartItem, ContactMessage, Order, Product


class CartAndOrderFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='customer', password='safe-pass-123')
        self.product = Product.objects.create(
            name='Rower testowy',
            price=Decimal('1200.00'),
            stock=3,
        )
        self.client = APIClient()

    def test_cart_and_order_models_can_be_created(self):
        cart = Cart.objects.create(user=self.user)
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('1200.00'),
        )

        self.assertIsNotNone(cart.pk)
        self.assertIsNotNone(order.pk)

    def test_cart_api_requires_authentication(self):
        response = self.client.get(reverse('get_cart'))

        self.assertIn(response.status_code, (401, 403))

    def test_add_product_then_create_order(self):
        self.client.force_authenticate(self.user)

        add_response = self.client.post(
            reverse('add_to_cart'),
            {'product_id': self.product.id, 'quantity': 2},
            format='json',
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(CartItem.objects.get().quantity, 2)

        order_response = self.client.post(reverse('create_order'), format='json')

        self.assertEqual(order_response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().total_price, Decimal('2400.00'))
        self.assertFalse(CartItem.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

    def test_cannot_add_more_than_available_stock(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            reverse('add_to_cart'),
            {'product_id': self.product.id, 'quantity': 4},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CartItem.objects.exists())

    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse('contact'),
            {
                'name': 'Jan',
                'email': 'jan@example.com',
                'subject': 'Pytanie o rower',
                'message': 'Czy ten model jest dostępny?',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertContains(response, 'Wiadomość została wysłana')

# Create your tests here.
