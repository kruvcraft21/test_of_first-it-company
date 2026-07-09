from django import forms
from django.core.exceptions import ValidationError
from .models import DDSRecord, Category, Subcategory


class DDSRecordAdminForm(forms.ModelForm):
    """
    Кастомная форма для DDSRecord с динамической подкатегорией.
    """

    class Meta:
        model = DDSRecord
        fields = ['date', 'status', 'transaction_type', 'category', 'subcategory', 'amount', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if self.instance.transaction_type:
                self.fields['category'].queryset = Category.objects.filter(
                    transaction_type=self.instance.transaction_type
                )
                if self.instance.category:
                    self.fields['subcategory'].queryset = Subcategory.objects.filter(
                        category=self.instance.category
                    )
        else:
            self.fields['category'].queryset = Category.objects.none()
            self.fields['subcategory'].queryset = Subcategory.objects.none()

        self.fields['amount'].widget.attrs['step'] = '0.01'
        self.fields['amount'].help_text = 'Сумма в рублях'
        self.fields['comment'].help_text = 'Необязательное поле'

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        amount = cleaned_data.get('amount')

        if category and transaction_type:
            if category.transaction_type != transaction_type:
                raise ValidationError(
                    f"Категория '{category.name}' не относится к типу "
                    f"'{transaction_type.name}'. Выберите корректную категорию."
                )

        if subcategory and category:
            if subcategory.category != category:
                raise ValidationError(
                    f"Подкатегория '{subcategory.name}' не относится к "
                    f"категории '{category.name}'. Выберите корректную подкатегорию."
                )

        if amount is not None and amount <= 0:
            raise ValidationError("Сумма должна быть больше нуля.")

        return cleaned_data

    def clean_category(self):
        category = self.cleaned_data.get('category')
        transaction_type = self.cleaned_data.get('transaction_type')

        if category and transaction_type:
            if category.transaction_type != transaction_type:
                raise ValidationError(
                    "Выберите категорию, которая относится к выбранному типу операции."
                )

        return category

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        category = self.cleaned_data.get('category')

        if subcategory and category:
            if subcategory.category != category:
                raise ValidationError(
                    "Выберите подкатегорию, которая относится к выбранной категории."
                )

        return subcategory
