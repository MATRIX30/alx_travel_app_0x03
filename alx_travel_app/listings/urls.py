from django.urls import path
from . import views

urlpatterns = [
    # Payment endpoints
    path('payments/initiate/', views.PaymentInitiateView.as_view(), name='payment_initiate'),
    path('payments/verify/', views.PaymentVerifyView.as_view(), name='payment_verify'),
    path('payments/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
    path('payments/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    
    # Payment status endpoints
    path('payments/<uuid:payment_id>/', views.get_payment_status, name='payment_status'),
    path('bookings/<uuid:booking_id>/payments/', views.get_booking_payments, name='booking_payments'),
]
