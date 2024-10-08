from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
import uuid

class OrderSerializerTestCase(APITestCase):

    def setUp(self):
        self.valid_order_data = {
            'order_number': str(uuid.uuid4()),
            'total_price': 10.0,
        }
        self.invalid_order_data_negative_price = {
            'order_number': str(uuid.uuid4()),
            'total_price': -5.0,
        }

    def test_valid_order_data(self):
        serializer = OrderSerializer(data=self.valid_order_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.total_price, self.valid_order_data['total_price'])

    def test_invalid_order_data_negative_price(self):
        serializer = OrderSerializer(data=self.invalid_order_data_negative_price)
        self.assertFalse(serializer.is_valid())
        self.assertIn('total_price', serializer.errors)

class OrderTestCase(APITestCase):

    def setUp(self):
        self.url = '/api/import-order/'
        self.valid_token = 'omni_pretest_token'
        self.invalid_token = 'invalid_token'
        self.valid_order_data = {
            'order_number': str(uuid.uuid4()),
            'total_price': 10.0,
        }
        self.invalid_order_data_negative_price = {
            'order_number': str(uuid.uuid4()),
            'total_price': -5.0,
        }

    def test_import_order_success(self):
        response = self.client.post(
            self.url,
            self.valid_order_data,
            format="json",
            HTTP_AUTHORIZATION=self.valid_token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  
        self.assertIn('order_id', response.data)  
        self.assertEqual(response.data['total_price'], self.valid_order_data['total_price'])

        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.total_price, self.valid_order_data['total_price'])

    def test_import_order_invalid_data_negative_price(self):
        response = self.client.post(
            self.url,
            self.invalid_order_data_negative_price,
            format="json",
            HTTP_AUTHORIZATION=self.valid_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn("error", response.data)
        self.assertIn("total_price", response.data["error"])

    def test_import_order_invalid_token(self):
        response = self.client.post(
            self.url,
            self.valid_order_data,
            format="json",
            HTTP_AUTHORIZATION=self.invalid_token
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid token")