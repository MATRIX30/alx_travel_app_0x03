from django.contrib import admin
from .models import Listing, Booking, Payment, Review

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['property_id', 'name', 'location', 'pricepernight', 'host', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['property_id', 'created_at', 'updated_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'property', 'status', 'check_in_date', 'check_out_date', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['user__username', 'user__email', 'property__name']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'booking_ref', 'amount', 'payment_status', 'payment_method', 'transaction_id', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'created_at', 'currency']
    search_fields = ['transaction_id', 'chapa_transaction_id', 'booking_ref__user__email']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing payment
            return list(self.readonly_fields) + ['booking_ref', 'amount', 'transaction_id']
        return self.readonly_fields

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'property__name', 'comment']
    readonly_fields = ['created_at']

# Register your models here.
