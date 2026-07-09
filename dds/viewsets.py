from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Status, TransactionType, Category, Subcategory, DDSRecord
from .serializers import (
    StatusSerializer, TransactionTypeSerializer, CategorySerializer,
    SubcategorySerializer, DDSRecordSerializer
)


class StatusViewSet(viewsets.ModelViewSet):
    """ViewSet for Status"""
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class TransactionTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for TransactionType"""
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type']
    search_fields = ['name']
    ordering_fields = ['name', 'transaction_type', 'created_at']


class SubcategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Subcategory"""
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__transaction_type']
    search_fields = ['name']
    ordering_fields = ['name', 'category', 'created_at']


class DDSRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for DDSRecord"""
    queryset = DDSRecord.objects.all()
    serializer_class = DDSRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'status', 'transaction_type', 'category', 'subcategory']
    search_fields = ['comment']
    ordering_fields = ['date', 'amount', 'created_at']
