from django.contrib import admin
from .models import Customer, Review, Order, OrderItem, Requisition

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'e_purse_balance', 'display_preferred_categories', 'display_preferred_writers')
    search_fields = ('user__username', 'user__email')

    def display_preferred_categories(self, obj):
        return ", ".join([cat.name for cat in obj.preferred_categories.all()])

    display_preferred_categories.short_description = 'Preferred Categories'

    def display_preferred_writers(self, obj):
        return ", ".join([writer.name for writer in obj.preferred_writers.all()])

    display_preferred_writers.short_description = 'Preferred Writers'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'book', 'rating', 'timestamp')
    search_fields = ('customer__user__username', 'book__name')
    list_filter = ('rating',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_price', 'status', 'payment_mode', 'timestamp')
    search_fields = ('customer__user__username',)
    list_filter = ('status', 'payment_mode')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'price')
    search_fields = ('order__customer__user__username', 'book__name')

@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'book', 'book_name', 'author_names', 'requested_at')
    search_fields = ('customer__user__username', 'book_name', 'author_names')
    list_filter = ('requested_at',)