from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()



class Listing(models.Model):
    property_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_properties')
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    location = models.CharField(max_length=255, null=False)
    pricepernight = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    property = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.property} ({self.status})"
    
    def get_total_nights(self):
        """Calculate total nights for the booking"""
        return (self.check_out_date - self.check_in_date).days

class Review(models.Model):
    property = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if not (1 <= self.rating <= 5):
            from django.core.exceptions import ValidationError
            raise ValidationError('Rating must be between 1 and 5.')

    def __str__(self):
        return f"{self.user} - {self.property} ({self.rating})"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('chapa', 'Chapa'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
    ]
    
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    booking_ref = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='chapa')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    chapa_transaction_id = models.CharField(max_length=255, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for payment details
    currency = models.CharField(max_length=3, default='ETB')
    payment_description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking_ref} ({self.payment_status})"
    
    def is_successful(self):
        """Check if payment is successful"""
        return self.payment_status == 'completed'
    
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.payment_status == 'completed' and self.amount > 0
    