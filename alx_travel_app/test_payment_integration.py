#!/usr/bin/env python
"""
Test script for Chapa payment integration
This script demonstrates the payment workflow for ALX Travel App
"""

import os
import sys
import django
import json
import requests
from datetime import date, timedelta

# Add the project directory to the Python path
sys.path.append('/home/cyanide/alx_proDev/alx_travel_app_0x02/alx_travel_app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from django.contrib.auth.models import User
from listings.models import Listing, Booking, Payment
from django.test import Client
from django.urls import reverse


def create_test_data():
    """Create test data for payment testing"""
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Create a test host
    host, created = User.objects.get_or_create(
        username='testhost',
        defaults={
            'email': 'host@example.com',
            'first_name': 'Test',
            'last_name': 'Host'
        }
    )
    
    # Create a test listing
    listing, created = Listing.objects.get_or_create(
        name='Beautiful Test Villa',
        defaults={
            'host': host,
            'description': 'A beautiful villa for testing payment integration',
            'location': 'Addis Ababa, Ethiopia',
            'pricepernight': 1500.00
        }
    )
    
    # Create a test booking
    check_in = date.today() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)
    total_amount = listing.pricepernight * 3  # 3 nights
    
    booking, created = Booking.objects.get_or_create(
        user=user,
        property=listing,
        check_in_date=check_in,
        check_out_date=check_out,
        defaults={
            'total_amount': total_amount,
            'status': 'pending'
        }
    )
    
    return user, listing, booking


def test_payment_initiation():
    """Test payment initiation"""
    
    print("=" * 60)
    print("TESTING PAYMENT INITIATION")
    print("=" * 60)
    
    # Create test data
    user, listing, booking = create_test_data()
    
    print(f"Created test booking: {booking.booking_id}")
    print(f"Booking amount: ETB {booking.total_amount}")
    print(f"Property: {listing.name}")
    print(f"User: {user.email}")
    
    # Test payment initiation
    client = Client()
    
    payment_data = {
        'booking_id': str(booking.booking_id)
    }
    
    try:
        response = client.post(
            '/api/payments/initiate/',
            data=json.dumps(payment_data),
            content_type='application/json'
        )
        
        print(f"\nPayment initiation response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✓ Payment initiation successful!")
            print(f"Payment ID: {response_data.get('payment_id')}")
            print(f"Transaction Reference: {response_data.get('tx_ref')}")
            print(f"Checkout URL: {response_data.get('checkout_url')}")
            
            # Check if payment record was created
            payment = Payment.objects.filter(
                transaction_id=response_data.get('tx_ref')
            ).first()
            
            if payment:
                print(f"✓ Payment record created in database")
                print(f"Payment Status: {payment.payment_status}")
                print(f"Payment Method: {payment.payment_method}")
                return payment
            else:
                print("✗ Payment record not found in database")
                
        else:
            print(f"✗ Payment initiation failed: {response.content}")
            
    except Exception as e:
        print(f"✗ Error during payment initiation: {str(e)}")
    
    return None


def test_payment_verification(payment):
    """Test payment verification"""
    
    print("\n" + "=" * 60)
    print("TESTING PAYMENT VERIFICATION")
    print("=" * 60)
    
    if not payment:
        print("✗ No payment to verify")
        return
    
    print(f"Verifying payment: {payment.transaction_id}")
    
    client = Client()
    
    verify_data = {
        'tx_ref': payment.transaction_id
    }
    
    try:
        response = client.post(
            '/api/payments/verify/',
            data=json.dumps(verify_data),
            content_type='application/json'
        )
        
        print(f"Payment verification response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✓ Payment verification successful!")
            print(f"Payment Status: {response_data.get('payment_status')}")
            print(f"Booking Status: {response_data.get('booking_status')}")
            
            # Refresh payment from database
            payment.refresh_from_db()
            print(f"Updated payment status in DB: {payment.payment_status}")
            
        else:
            print(f"✗ Payment verification failed: {response.content}")
            
    except Exception as e:
        print(f"✗ Error during payment verification: {str(e)}")


def test_payment_status_api():
    """Test payment status API endpoints"""
    
    print("\n" + "=" * 60)
    print("TESTING PAYMENT STATUS APIs")
    print("=" * 60)
    
    # Get all payments
    payments = Payment.objects.all()
    
    if not payments:
        print("✗ No payments found to test")
        return
    
    payment = payments.first()
    booking = payment.booking_ref
    
    print(f"Testing with Payment ID: {payment.payment_id}")
    print(f"Testing with Booking ID: {booking.booking_id}")
    
    client = Client()
    
    # Test payment status endpoint
    try:
        response = client.get(f'/api/payments/{payment.payment_id}/')
        print(f"Payment status API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Payment status API working!")
            print(f"Payment Status: {data.get('payment_status')}")
            print(f"Amount: {data.get('amount')}")
        else:
            print(f"✗ Payment status API failed: {response.content}")
            
    except Exception as e:
        print(f"✗ Error testing payment status API: {str(e)}")
    
    # Test booking payments endpoint
    try:
        response = client.get(f'/api/bookings/{booking.booking_id}/payments/')
        print(f"Booking payments API response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Booking payments API working!")
            print(f"Number of payments: {len(data)}")
        else:
            print(f"✗ Booking payments API failed: {response.content}")
            
    except Exception as e:
        print(f"✗ Error testing booking payments API: {str(e)}")


def print_summary():
    """Print summary of test results"""
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    # Count objects
    users = User.objects.count()
    listings = Listing.objects.count()
    bookings = Booking.objects.count()
    payments = Payment.objects.count()
    
    print(f"Total Users: {users}")
    print(f"Total Listings: {listings}")
    print(f"Total Bookings: {bookings}")
    print(f"Total Payments: {payments}")
    
    # Payment status breakdown
    payment_statuses = Payment.objects.values_list('payment_status', flat=True)
    status_counts = {}
    for status in payment_statuses:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nPayment Status Breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    print("ALX Travel App - Chapa Payment Integration Test")
    print("=" * 60)
    
    # Test payment initiation
    payment = test_payment_initiation()
    
    # Test payment verification
    test_payment_verification(payment)
    
    # Test payment status APIs
    test_payment_status_api()
    
    # Print summary
    print_summary()
    
    print("\nNote: This test uses sandbox/test data.")
    print("For actual payment processing, use Chapa's sandbox environment.")
    print("Real payment verification requires actual Chapa API responses.")
