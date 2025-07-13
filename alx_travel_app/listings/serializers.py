from rest_framework import serializers
from .models import Listing, Booking, Payment, Review

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    total_nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = '__all__'
    
    def get_total_nights(self, obj):
        return obj.get_total_nights()

class PaymentSerializer(serializers.ModelSerializer):
    booking_details = BookingSerializer(source='booking_ref', read_only=True)
    is_successful = serializers.SerializerMethodField()
    can_be_refunded = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'booking_ref', 'amount', 'payment_status', 
            'payment_method', 'transaction_id', 'chapa_transaction_id',
            'payment_date', 'created_at', 'updated_at', 'currency',
            'payment_description', 'failure_reason', 'booking_details',
            'is_successful', 'can_be_refunded'
        ]
        read_only_fields = ['payment_id', 'created_at', 'updated_at']
    
    def get_is_successful(self, obj):
        return obj.is_successful()
    
    def get_can_be_refunded(self, obj):
        return obj.can_be_refunded()

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
