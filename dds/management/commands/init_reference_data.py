from django.core.management.base import BaseCommand
from dds.models import Status, TransactionType, Category, Subcategory


class Command(BaseCommand):
    help = "Creates required reference data from the assignment"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating reference data..."))

        business, _ = Status.objects.get_or_create(name="Бизнес")
        personal, _ = Status.objects.get_or_create(name="Личное")
        tax, _ = Status.objects.get_or_create(name="Налог")

        replenishment, _ = TransactionType.objects.get_or_create(name="Пополнение")
        writeoff, _ = TransactionType.objects.get_or_create(name="Списание")

        infrastructure, _ = Category.objects.get_or_create(
            name="Инфраструктура",
            transaction_type=writeoff,
        )
        marketing, _ = Category.objects.get_or_create(
            name="Маркетинг",
            transaction_type=writeoff,
        )

        Subcategory.objects.get_or_create(name="VPS", category=infrastructure)
        Subcategory.objects.get_or_create(name="Proxy", category=infrastructure)
        Subcategory.objects.get_or_create(name="Farpost", category=marketing)
        Subcategory.objects.get_or_create(name="Avito", category=marketing)

        self.stdout.write(self.style.SUCCESS("Reference data created successfully."))