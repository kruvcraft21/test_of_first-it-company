from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

# Create router for API endpoints
router = DefaultRouter()
router.register(r'statuses', viewsets.StatusViewSet, basename='status')
router.register(r'transaction-types', viewsets.TransactionTypeViewSet, basename='transaction-type')
router.register(r'categories', viewsets.CategoryViewSet, basename='category')
router.register(r'subcategories', viewsets.SubcategoryViewSet, basename='subcategory')
router.register(r'records', viewsets.DDSRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
]
