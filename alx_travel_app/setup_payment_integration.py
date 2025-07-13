#!/usr/bin/env python
"""
Setup script for ALX Travel App Payment Integration
This script sets up the database and runs initial tests
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a shell command and print the result"""
    print(f"\n{description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd='/home/cyanide/alx_proDev/alx_travel_app_0x02/alx_travel_app'
        )
        
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Error running command: {str(e)}")
        return False

def main():
    """Main setup function"""
    
    print("=" * 60)
    print("ALX TRAVEL APP - PAYMENT INTEGRATION SETUP")
    print("=" * 60)
    
    # Step 1: Install required packages
    packages = [
        'django',
        'djangorestframework',
        'python-dotenv',
        'requests',
        'django-chapa'
    ]
    
    for package in packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    # Step 2: Make migrations
    run_command("python manage.py makemigrations", "Creating migrations")
    
    # Step 3: Run migrations
    run_command("python manage.py migrate", "Running migrations")
    
    # Step 4: Create superuser (non-interactive)
    run_command(
        "python manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin user already exists')\"",
        "Creating admin user"
    )
    
    # Step 5: Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Step 6: Run tests
    run_command("python manage.py check", "Running Django system checks")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETED")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access admin panel: http://127.0.0.1:8000/admin/")
    print("3. Login with: admin / admin123")
    print("4. Test payment APIs using the provided endpoints")
    print("5. Run the payment integration test: python test_payment_integration.py")
    
    print("\nPayment API Endpoints:")
    print("- POST /api/payments/initiate/ - Initiate payment")
    print("- POST /api/payments/verify/ - Verify payment")
    print("- GET /api/payments/<payment_id>/ - Get payment status")
    print("- GET /api/bookings/<booking_id>/payments/ - Get booking payments")
    
    print("\nEnvironment Variables Required:")
    print("- CHAPA_SECRET_KEY: Your Chapa secret key")
    print("- CHAPA_PUBLIC_KEY: Your Chapa public key")
    print("- CHAPA_ENCRYPTION_KEY: Your Chapa encryption key")
    print("- SECRET_KEY: Django secret key")
    print("- DEBUG: Set to False in production")

if __name__ == "__main__":
    main()
