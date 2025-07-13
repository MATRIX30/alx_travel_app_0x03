from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import requests
import uuid
from decimal import Decimal
from .models import Booking, Payment, Listing
from .serializers import BookingSerializer, PaymentSerializer
import logging

logger = logging.getLogger(__name__)

# Chapa API Configuration
CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify"


class PaymentInitiateView(View):
    """
    API endpoint to initiate payment with Chapa
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            
            if not booking_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Booking ID is required'
                }, status=400)
            
            # Get booking details
            booking = get_object_or_404(Booking, booking_id=booking_id)
            
            # Generate unique transaction reference
            tx_ref = f"tx_{uuid.uuid4().hex[:16]}"
            
            # Create payment record
            payment = Payment.objects.create(
                booking_ref=booking,
                amount=booking.total_amount,
                transaction_id=tx_ref,
                payment_status='pending',
                payment_method='chapa',
                currency='ETB',
                payment_description=f'Payment for booking {booking.booking_id}'
            )
            
            # Prepare Chapa payment data
            chapa_data = {
                "amount": str(booking.total_amount),
                "currency": "ETB",
                "email": booking.user.email,
                "first_name": booking.user.first_name,
                "last_name": booking.user.last_name,
                "phone_number": getattr(booking.user, 'phone_number', ''),
                "tx_ref": tx_ref,
                "callback_url": f"{request.build_absolute_uri('/api/payments/callback/')}",
                "return_url": f"{request.build_absolute_uri('/api/payments/success/')}",
                "description": f"Payment for {booking.property.name} booking",
                "customization": {
                    "title": "ALX Travel App",
                    "description": f"Payment for {booking.property.name}"
                }
            }
            
            # Make request to Chapa API
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(CHAPA_API_URL, json=chapa_data, headers=headers)
            
            if response.status_code == 200:
                chapa_response = response.json()
                
                if chapa_response.get('status') == 'success':
                    # Update payment with Chapa transaction ID
                    payment.chapa_transaction_id = chapa_response['data']['tx_ref']
                    payment.payment_status = 'processing'
                    payment.save()
                    
                    return JsonResponse({
                        'success': True,
                        'payment_id': str(payment.payment_id),
                        'checkout_url': chapa_response['data']['checkout_url'],
                        'tx_ref': tx_ref,
                        'message': 'Payment initiated successfully'
                    })
                else:
                    payment.payment_status = 'failed'
                    payment.failure_reason = chapa_response.get('message', 'Unknown error')
                    payment.save()
                    
                    return JsonResponse({
                        'success': False,
                        'error': chapa_response.get('message', 'Payment initiation failed')
                    }, status=400)
            else:
                payment.payment_status = 'failed'
                payment.failure_reason = f'HTTP {response.status_code}: {response.text}'
                payment.save()
                
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to communicate with payment gateway'
                }, status=500)
                
        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class PaymentVerifyView(View):
    """
    API endpoint to verify payment status with Chapa
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            tx_ref = data.get('tx_ref')
            
            if not tx_ref:
                return JsonResponse({
                    'success': False,
                    'error': 'Transaction reference is required'
                }, status=400)
            
            # Get payment record
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
            except Payment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Payment not found'
                }, status=404)
            
            # Verify payment with Chapa
            verify_url = f"{CHAPA_VERIFY_URL}/{tx_ref}"
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(verify_url, headers=headers)
            
            if response.status_code == 200:
                chapa_response = response.json()
                
                if chapa_response.get('status') == 'success':
                    payment_data = chapa_response['data']
                    
                    # Update payment status based on Chapa response
                    if payment_data.get('status') == 'success':
                        payment.payment_status = 'completed'
                        payment.payment_date = timezone.now()
                        
                        # Update booking status
                        booking = payment.booking_ref
                        booking.status = 'confirmed'
                        booking.save()
                        
                        # Send confirmation email (you can use Celery for background task)
                        self.send_confirmation_email(payment)
                        
                    elif payment_data.get('status') == 'failed':
                        payment.payment_status = 'failed'
                        payment.failure_reason = payment_data.get('message', 'Payment failed')
                    
                    payment.save()
                    
                    return JsonResponse({
                        'success': True,
                        'payment_status': payment.payment_status,
                        'booking_status': payment.booking_ref.status,
                        'message': 'Payment status updated successfully'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': chapa_response.get('message', 'Verification failed')
                    }, status=400)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to verify payment'
                }, status=500)
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def send_confirmation_email(self, payment):
        """
        Send confirmation email to user
        """
        try:
            booking = payment.booking_ref
            subject = f'Booking Confirmation - {booking.property.name}'
            message = f"""
            Dear {booking.user.first_name},
            
            Your booking has been confirmed!
            
            Booking Details:
            - Property: {booking.property.name}
            - Location: {booking.property.location}
            - Check-in: {booking.check_in_date}
            - Check-out: {booking.check_out_date}
            - Total Amount: ETB {payment.amount}
            - Payment ID: {payment.payment_id}
            
            Thank you for choosing ALX Travel App!
            
            Best regards,
            ALX Travel Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
                fail_silently=False,
            )
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")


class PaymentCallbackView(View):
    """
    Webhook endpoint for Chapa payment callbacks
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            tx_ref = data.get('tx_ref')
            
            if tx_ref:
                # Verify payment automatically
                verify_view = PaymentVerifyView()
                verify_request = type('Request', (), {
                    'body': json.dumps({'tx_ref': tx_ref}).encode(),
                    'method': 'POST'
                })()
                
                verify_view.post(verify_request)
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Payment callback error: {str(e)}")
            return JsonResponse({'success': False}, status=500)


class PaymentSuccessView(View):
    """
    Success page after payment completion
    """
    
    def get(self, request):
        return render(request, 'payments/success.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, payment_id):
    """
    Get payment status by payment ID
    """
    try:
        payment = get_object_or_404(Payment, payment_id=payment_id)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_payments(request, booking_id):
    """
    Get all payments for a specific booking
    """
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        payments = Payment.objects.filter(booking_ref=booking)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)


# Create your views here.
