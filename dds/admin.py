from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Status, TransactionType, Category, Subcategory, DDSRecord
from .forms import DDSRecordAdminForm


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """Admin for Status reference dictionary"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    """Admin for TransactionType"""
    list_display = ('name', 'category_count', 'description', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'category_count')
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Статистика', {
            'fields': ('category_count',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def category_count(self, obj):
        """Display count of categories"""
        count = obj.categories.count()
        return format_html(
            '<span style="background-color: #e8f4f8; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    category_count.short_description = 'Категорий'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category"""
    list_display = ('name', 'transaction_type', 'subcategory_count', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('name', 'transaction_type__name')
    readonly_fields = ('created_at', 'subcategory_count')
    ordering = ('transaction_type', 'name')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'transaction_type', 'description')
        }),
        ('Статистика', {
            'fields': ('subcategory_count',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def subcategory_count(self, obj):
        """Display count of subcategories"""
        count = obj.subcategories.count()
        return format_html(
            '<span style="background-color: #f0e8f4; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    subcategory_count.short_description = 'Подкатегорий'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Admin for Subcategory"""
    list_display = ('name', 'category', 'transaction_type', 'created_at')
    list_filter = ('category__transaction_type', 'category', 'created_at')
    search_fields = ('name', 'category__name')
    readonly_fields = ('created_at', 'transaction_type')
    ordering = ('category', 'name')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description')
        }),
        ('Связанные данные', {
            'fields': ('transaction_type',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def transaction_type(self, obj):
        """Display transaction type for the subcategory"""
        return obj.category.transaction_type
    transaction_type.short_description = 'Тип операции'


@admin.register(DDSRecord)
class DDSRecordAdmin(admin.ModelAdmin):
    """Admin for DDSRecord"""
    form = DDSRecordAdminForm

    list_display = (
        'date', 'status_badge', 'transaction_type', 'category', 'amount_display',
        'comment_short'
    )
    list_filter = (
        'date', 'status', 'transaction_type', 'category', 'subcategory', 'created_at'
    )
    search_fields = ('comment', 'category__name', 'subcategory__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')

    fieldsets = (
        ('Основная информация о записи', {
            'fields': ('date', 'status', 'amount', 'comment')
        }),
        ('Категоризация (иерархия: Тип → Категория → Подкатегория)', {
            'fields': ('transaction_type', 'category', 'subcategory'),
            'description': 'Выберите тип, затем категорию, связанную с этим типом, '
                          'и подкатегорию, связанную с выбранной категорией.'
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'Business': '#e8f4f8',
            'Personal': '#f0e8f4',
            'Tax': '#f4f0e8',
        }
        color = colors.get(obj.status.name, '#f0f0f0')
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; '
            'font-weight: bold;">{}</span>',
            color,
            obj.status.name
        )
    status_badge.short_description = 'Статус'

    def amount_display(self, obj):
        amount_str = f"{obj.amount:,.2f}".replace(',', ' ')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} р.</span>',
            '#28a745' if obj.transaction_type.name == 'Пополнение' else '#dc3545',
            amount_str
        )
    amount_display.short_description = 'Сумма'

    def comment_short(self, obj):
        if obj.comment:
            short_comment = obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
            return short_comment
        return '—'
    comment_short.short_description = 'Комментарий'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'status', 'transaction_type', 'category', 'subcategory'
        )

    actions = ['export_to_csv']

    def export_to_csv(self, request, queryset):
        """Action to export to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dds_records.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Дата', 'Статус', 'Тип', 'Категория', 'Подкатегория', 'Сумма', 'Комментарий'
        ])

        for record in queryset:
            writer.writerow([
                record.date,
                record.status.name,
                record.transaction_type.name,
                record.category.name,
                record.subcategory.name,
                record.amount,
                record.comment
            ])

        return response

    export_to_csv.short_description = "Экспортировать выбранные записи в CSV"

