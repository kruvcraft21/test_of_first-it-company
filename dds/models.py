from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Status(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Статус"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ['name']

    def __str__(self):
        return self.name


class TransactionType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Тип"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Категория"
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name='categories',
        verbose_name="Тип операции"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['transaction_type', 'name']
        unique_together = ['name', 'transaction_type']

    def __str__(self):
        return f"{self.name} ({self.transaction_type})"


class Subcategory(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Подкатегория"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='subcategories',
        verbose_name="Категория"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ['category', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class DDSRecord(models.Model):
    date = models.DateField(
        default=timezone.now,
        verbose_name="Дата"
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name="Статус"
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name="Тип"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name="Подкатегория"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма (руб.)"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.date} - {self.transaction_type} - {self.amount} р."

    def clean(self):

        errors = {}


        if self.amount is not None and self.amount <= 0:
            errors['amount'] = "Сумма должна быть больше нуля."

        if self.category and self.transaction_type:
            if self.category.transaction_type != self.transaction_type:
                errors['category'] = (
                    f"Категория '{self.category.name}' не относится к типу "
                    f"'{self.transaction_type.name}'. "
                    f"Выберите категорию из списка доступных."
                )


        if self.subcategory and self.category:
            if self.subcategory.category != self.category:
                errors['subcategory'] = (
                    f"Подкатегория '{self.subcategory.name}' не относится к "
                    f"категории '{self.category.name}'. "
                    f"Выберите подкатегорию из списка доступных."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
