from rest_framework import serializers
from .models import Status, TransactionType, Category, Subcategory, DDSRecord


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']


class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']


class CategorySerializer(serializers.ModelSerializer):
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'transaction_type', 'transaction_type_name', 'description', 'created_at']
        read_only_fields = ['created_at']


class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_name', 'description', 'created_at']
        read_only_fields = ['created_at']


class DDSRecordSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = DDSRecord
        fields = [
            'id', 'date', 'status', 'status_name', 'transaction_type', 'transaction_type_name',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'amount', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        errors = {}

        # Validate category belongs to transaction type
        if 'category' in data and 'transaction_type' in data:
            category = data['category']
            transaction_type = data['transaction_type']
            if category.transaction_type != transaction_type:
                errors['category'] = (
                    f"Категория '{category.name}' не относится к типу "
                    f"'{transaction_type.name}'."
                )

        if 'subcategory' in data and 'category' in data:
            subcategory = data['subcategory']
            category = data['category']
            if subcategory.category != category:
                errors['subcategory'] = (
                    f"Подкатегория '{subcategory.name}' не относится к "
                    f"категории '{category.name}'."
                )

        if 'amount' in data and data['amount'] <= 0:
            errors['amount'] = "Сумма должна быть больше нуля."

        if errors:
            raise serializers.ValidationError(errors)

        return data
