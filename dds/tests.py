from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Status, TransactionType, Category, Subcategory, DDSRecord


class StatusModelTest(TestCase):
    """Tests for Status model"""

    def setUp(self):
        self.status = Status.objects.create(
            name="Business",
            description="Business transactions"
        )

    def test_status_creation(self):
        self.assertEqual(self.status.name, "Business")
        self.assertTrue(self.status.created_at)

    def test_status_string_representation(self):
        self.assertEqual(str(self.status), "Business")

    def test_status_unique_name(self):
        with self.assertRaises(Exception):
            Status.objects.create(name="Business")


class TransactionTypeModelTest(TestCase):
    """Tests for TransactionType model"""

    def setUp(self):
        self.tx_type = TransactionType.objects.create(
            name="Пополнение",
            description="Money replenishment"
        )

    def test_transaction_type_creation(self):
        self.assertEqual(self.tx_type.name, "Пополнение")

    def test_transaction_type_string_representation(self):
        self.assertEqual(str(self.tx_type), "Пополнение")


class CategoryModelTest(TestCase):
    """Tests for Category model"""

    def setUp(self):
        self.tx_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.tx_type,
            description="Marketing expenses"
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Маркетинг")
        self.assertEqual(self.category.transaction_type, self.tx_type)

    def test_category_string_representation(self):
        expected = f"Маркетинг ({self.tx_type})"
        self.assertEqual(str(self.category), expected)

    def test_category_unique_together(self):
        with self.assertRaises(Exception):
            Category.objects.create(
                name="Маркетинг",
                transaction_type=self.tx_type
            )


class SubcategoryModelTest(TestCase):
    """Tests for Subcategory model"""

    def setUp(self):
        self.tx_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.tx_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Farpost",
            category=self.category
        )

    def test_subcategory_creation(self):
        self.assertEqual(self.subcategory.name, "Farpost")
        self.assertEqual(self.subcategory.category, self.category)

    def test_subcategory_string_representation(self):
        expected = f"Farpost ({self.category.name})"
        self.assertEqual(str(self.subcategory), expected)


class DDSRecordModelTest(TestCase):
    """Tests for DDSRecord model with validation"""

    def setUp(self):
        self.status = Status.objects.create(name="Business")
        self.tx_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.tx_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Farpost",
            category=self.category
        )

    def test_record_creation(self):
        """Test creating a valid record"""
        record = DDSRecord.objects.create(
            status=self.status,
            transaction_type=self.tx_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=1000.00,
            comment="Test transaction"
        )
        self.assertEqual(record.amount, 1000.00)

    def test_record_negative_amount(self):
        record = DDSRecord(
            status=self.status,
            transaction_type=self.tx_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=-100.00
        )
        with self.assertRaises(ValidationError):
            record.save()

    def test_record_invalid_category_for_type(self):
        other_type = TransactionType.objects.create(name="Пополнение")
        wrong_category = Category.objects.create(
            name="Infrastructure",
            transaction_type=other_type
        )
        wrong_subcategory = Subcategory.objects.create(
            name="VPS",
            category=wrong_category
        )

        record = DDSRecord(
            status=self.status,
            transaction_type=self.tx_type,
            category=wrong_category,  # Wrong type
            subcategory=wrong_subcategory,
            amount=1000.00
        )
        with self.assertRaises(ValidationError) as cm:
            record.save()
        self.assertIn('category', cm.exception.error_dict)

    def test_record_invalid_subcategory_for_category(self):
        other_category = Category.objects.create(
            name="Infrastructure",
            transaction_type=self.tx_type
        )
        wrong_subcategory = Subcategory.objects.create(
            name="VPS",
            category=other_category
        )

        record = DDSRecord(
            status=self.status,
            transaction_type=self.tx_type,
            category=self.category,
            subcategory=wrong_subcategory,  # Wrong category
            amount=1000.00
        )
        with self.assertRaises(ValidationError) as cm:
            record.save()
        self.assertIn('subcategory', cm.exception.error_dict)

    def test_record_string_representation(self):
        record = DDSRecord.objects.create(
            status=self.status,
            transaction_type=self.tx_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=500.50
        )
        self.assertIn("500.5", str(record))


class AdminIntegrationTest(TestCase):
    """Tests for Django admin integration"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')

        self.status = Status.objects.create(name="Business")
        self.tx_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.tx_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Farpost",
            category=self.category
        )

    def test_admin_status_page(self):
        response = self.client.get('/admin/dds/status/')
        self.assertEqual(response.status_code, 200)

    def test_admin_record_page(self):
        response = self.client.get('/admin/dds/ddsrecord/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_add_record(self):
        response = self.client.get('/admin/dds/ddsrecord/add/')
        self.assertEqual(response.status_code, 200)


class APITestCase(TestCase):
    """Tests for REST API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.status = Status.objects.create(name="Business")
        self.tx_type = TransactionType.objects.create(name="Списание")
        self.category = Category.objects.create(
            name="Маркетинг",
            transaction_type=self.tx_type
        )
        self.subcategory = Subcategory.objects.create(
            name="Farpost",
            category=self.category
        )

    def test_status_list_api(self):
        response = self.client.get('/api/statuses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_transaction_type_list_api(self):
        response = self.client.get('/api/transaction-types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_record_create_api_valid(self):
        data = {
            'status': self.status.id,
            'transaction_type': self.tx_type.id,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'amount': 1000.00,
            'comment': 'Test via API'
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_record_create_api_invalid_category(self):
        other_type = TransactionType.objects.create(name="Пополнение")
        wrong_category = Category.objects.create(
            name="Infrastructure",
            transaction_type=other_type
        )
        wrong_subcategory = Subcategory.objects.create(
            name="VPS",
            category=wrong_category
        )

        data = {
            'status': self.status.id,
            'transaction_type': self.tx_type.id,
            'category': wrong_category.id,
            'subcategory': wrong_subcategory.id,
            'amount': 1000.00
        }
        response = self.client.post('/api/records/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_record_filter_by_status(self):
        DDSRecord.objects.create(
            status=self.status,
            transaction_type=self.tx_type,
            category=self.category,
            subcategory=self.subcategory,
            amount=500.00
        )
        response = self.client.get(f'/api/records/?status={self.status.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

