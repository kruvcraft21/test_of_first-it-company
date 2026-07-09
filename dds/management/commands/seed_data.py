"""
Management command to populate initial data for demonstration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dds.models import Status, TransactionType, Category, Subcategory, DDSRecord
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populates the database with initial sample data'

    def handle(self, *args, **options):
        """Create sample data"""
        self.stdout.write(self.style.SUCCESS('Initial data...'))

        self.stdout.write('Creating statuses...')
        business_status, _ = Status.objects.get_or_create(
            name='Бизнес',
            defaults={'description': 'Бизнес транзакции'}
        )
        personal_status, _ = Status.objects.get_or_create(
            name='Личное',
            defaults={'description': 'Личные транзакции'}
        )
        tax_status, _ = Status.objects.get_or_create(
            name='Налог',
            defaults={'description': 'Налоговые транзакции'}
        )

        self.stdout.write('Creating transaction types...')
        replenishment_type, _ = TransactionType.objects.get_or_create(
            name='Пополнение',
            defaults={'description': 'Пополнение средств'}
        )
        writeoff_type, _ = TransactionType.objects.get_or_create(
            name='Списание',
            defaults={'description': 'Списание средств'}
        )

        self.stdout.write('Creating categories for transaction...')
        sales_category, _ = Category.objects.get_or_create(
            name='Продажи',
            transaction_type=replenishment_type,
            defaults={'description': 'Доходы от продаж'}
        )
        investment_category, _ = Category.objects.get_or_create(
            name='Инвестиции',
            transaction_type=replenishment_type,
            defaults={'description': 'Доходы от инвестиций'}
        )

        self.stdout.write('Creating categories for write-off...')
        infrastructure_category, _ = Category.objects.get_or_create(
            name='Инфраструктура',
            transaction_type=writeoff_type,
            defaults={'description': 'Расходы на инфраструктуру'}
        )
        marketing_category, _ = Category.objects.get_or_create(
            name='Маркетинг',
            transaction_type=writeoff_type,
            defaults={'description': 'Расходы на маркетинг'}
        )
        salary_category, _ = Category.objects.get_or_create(
            name='Зарплата',
            transaction_type=writeoff_type,
            defaults={'description': 'Расходы на зарплату'}
        )

        self.stdout.write('Creating subcategories...')
        vps_subcategory, _ = Subcategory.objects.get_or_create(
            name='VPS',
            category=infrastructure_category,
            defaults={'description': 'Virtual Private Server'}
        )
        proxy_subcategory, _ = Subcategory.objects.get_or_create(
            name='Proxy',
            category=infrastructure_category,
            defaults={'description': 'Proxy services'}
        )
        domain_subcategory, _ = Subcategory.objects.get_or_create(
            name='Домены',
            category=infrastructure_category,
            defaults={'description': 'Domain names'}
        )

        farpost_subcategory, _ = Subcategory.objects.get_or_create(
            name='Farpost',
            category=marketing_category,
            defaults={'description': 'Farpost рекламка'}
        )
        avito_subcategory, _ = Subcategory.objects.get_or_create(
            name='Avito',
            category=marketing_category,
            defaults={'description': 'Avito рекламка'}
        )
        google_ads_subcategory, _ = Subcategory.objects.get_or_create(
            name='Google Ads',
            category=marketing_category,
            defaults={'description': 'Google Ads campaigns'}
        )

        online_sales_subcategory, _ = Subcategory.objects.get_or_create(
            name='Онлайн продажи',
            category=sales_category,
            defaults={'description': 'Онлайн продажи'}
        )
        consultation_subcategory, _ = Subcategory.objects.get_or_create(
            name='Консультации',
            category=sales_category,
            defaults={'description': 'Консультации'}
        )

        # Create Subcategories for Salary
        salary_subcategory, _ = Subcategory.objects.get_or_create(
            name='Зарплата сотрудников',
            category=salary_category,
            defaults={'description': 'Зарплата сотрудников компании'}
        )

        # Create sample records
        self.stdout.write('Creating sample records...')
        today = timezone.now().date()

        sample_records = [
            {
                'date': today - timedelta(days=5),
                'status': business_status,
                'transaction_type': writeoff_type,
                'category': infrastructure_category,
                'subcategory': vps_subcategory,
                'amount': 5000.00,
                'comment': 'VPS hosting на одни месяц'
            },
            {
                'date': today - timedelta(days=4),
                'status': business_status,
                'transaction_type': writeoff_type,
                'category': marketing_category,
                'subcategory': farpost_subcategory,
                'amount': 2500.00,
                'comment': 'Farpost рекламка'
            },
            {
                'date': today - timedelta(days=3),
                'status': business_status,
                'transaction_type': replenishment_type,
                'category': sales_category,
                'subcategory': online_sales_subcategory,
                'amount': 15000.00,
                'comment': 'Онлайн продажи'
            },
            {
                'date': today - timedelta(days=2),
                'status': business_status,
                'transaction_type': writeoff_type,
                'category': marketing_category,
                'subcategory': google_ads_subcategory,
                'amount': 3000.00,
                'comment': 'Месечный бюджет в Google Ads'
            },
            {
                'date': today - timedelta(days=1),
                'status': personal_status,
                'transaction_type': writeoff_type,
                'category': infrastructure_category,
                'subcategory': proxy_subcategory,
                'amount': 1200.00,
                'comment': 'Proxy service подписка'
            },
            {
                'date': today,
                'status': business_status,
                'transaction_type': writeoff_type,
                'category': salary_category,
                'subcategory': salary_subcategory,
                'amount': 50000.00,
                'comment': 'Месечная зарплата сотрудников'
            },
        ]

        for record_data in sample_records:
            DDSRecord.objects.get_or_create(
                date=record_data['date'],
                status=record_data['status'],
                transaction_type=record_data['transaction_type'],
                category=record_data['category'],
                subcategory=record_data['subcategory'],
                amount=record_data['amount'],
                defaults={'comment': record_data['comment']}
            )

        self.stdout.write(self.style.SUCCESS('✓ Successfully created all sample data!'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  • Statuses: {Status.objects.count()}')
        self.stdout.write(f'  • Transaction Types: {TransactionType.objects.count()}')
        self.stdout.write(f'  • Categories: {Category.objects.count()}')
        self.stdout.write(f'  • Subcategories: {Subcategory.objects.count()}')
        self.stdout.write(f'  • Records: {DDSRecord.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Access admin panel at: http://localhost:8000/admin/'))
