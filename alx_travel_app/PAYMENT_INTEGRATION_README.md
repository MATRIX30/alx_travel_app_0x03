# ALX Travel App - Payment Integration with Chapa

## Overview

This project implements a complete payment integration system using the Chapa payment gateway for the ALX Travel App. The system handles booking payments, payment verification, and status updates.

## Features

- **Payment Initiation**: Create payment requests with Chapa API
- **Payment Verification**: Verify payment status with Chapa
- **Payment Status Tracking**: Track payment status throughout the lifecycle
- **Booking Management**: Integrate payments with booking system
- **Email Notifications**: Send confirmation emails on successful payments
- **Admin Interface**: Manage payments through Django admin
- **REST API**: Complete API endpoints for payment operations

## Models

### Payment Model
- `payment_id`: UUID primary key
- `booking_ref`: Foreign key to Booking
- `amount`: Payment amount
- `payment_status`: Status (pending, processing, completed, failed, cancelled, refunded)
- `payment_method`: Payment method (chapa, bank_transfer, etc.)
- `transaction_id`: Unique transaction reference
- `chapa_transaction_id`: Chapa-specific transaction ID
- `payment_date`: Completion date
- `currency`: Payment currency (default: ETB)
- `payment_description`: Description of payment
- `failure_reason`: Reason for failure (if applicable)

### Enhanced Booking Model
- `booking_id`: UUID primary key
- `check_in_date`: Check-in date
- `check_out_date`: Check-out date
- `total_amount`: Total booking amount
- Additional fields for payment integration

## API Endpoints

### Payment Endpoints

#### 1. Initiate Payment
```
POST /api/payments/initiate/
```

**Request Body:**
```json
{
    "booking_id": "uuid-of-booking"
}
```

**Response:**
```json
{
    "success": true,
    "payment_id": "uuid-of-payment",
    "checkout_url": "https://checkout.chapa.co/...",
    "tx_ref": "transaction-reference",
    "message": "Payment initiated successfully"
}
```

#### 2. Verify Payment
```
POST /api/payments/verify/
```

**Request Body:**
```json
{
    "tx_ref": "transaction-reference"
}
```

**Response:**
```json
{
    "success": true,
    "payment_status": "completed",
    "booking_status": "confirmed",
    "message": "Payment status updated successfully"
}
```

#### 3. Get Payment Status
```
GET /api/payments/{payment_id}/
```

**Response:**
```json
{
    "payment_id": "uuid",
    "booking_ref": "uuid",
    "amount": "1500.00",
    "payment_status": "completed",
    "payment_method": "chapa",
    "transaction_id": "tx_ref",
    "payment_date": "2025-01-01T10:00:00Z",
    "currency": "ETB",
    "is_successful": true,
    "can_be_refunded": true,
    "booking_details": {
        "booking_id": "uuid",
        "property_name": "Beautiful Villa",
        "user_email": "user@example.com",
        "check_in_date": "2025-01-10",
        "check_out_date": "2025-01-13",
        "total_nights": 3
    }
}
```

#### 4. Get Booking Payments
```
GET /api/bookings/{booking_id}/payments/
```

**Response:**
```json
[
    {
        "payment_id": "uuid",
        "amount": "1500.00",
        "payment_status": "completed",
        "payment_method": "chapa",
        "created_at": "2025-01-01T10:00:00Z"
    }
]
```

## Environment Variables

Create a `.env` file in your project root:

```env
# Django Configuration
SECRET_KEY=your-django-secret-key
DEBUG=False

# Chapa API Configuration
CHAPA_SECRET_KEY=your-chapa-secret-key
CHAPA_PUBLIC_KEY=your-chapa-public-key
CHAPA_ENCRYPTION_KEY=your-chapa-encryption-key

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com

# Database Configuration (if using external database)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Setup Instructions

1. **Install Dependencies**
```bash
pip install django djangorestframework python-dotenv requests django-chapa
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. **Run Setup Script**
```bash
python setup_payment_integration.py
```

4. **Start Development Server**
```bash
python manage.py runserver
```

5. **Test Payment Integration**
```bash
python test_payment_integration.py
```

## Payment Workflow

1. **User Creates Booking**: User selects property and dates
2. **Payment Initiation**: System creates payment record and requests Chapa checkout URL
3. **User Completes Payment**: User is redirected to Chapa checkout page
4. **Payment Verification**: System verifies payment status with Chapa
5. **Booking Confirmation**: On successful payment, booking is confirmed
6. **Email Notification**: Confirmation email is sent to user
7. **Status Updates**: Payment and booking statuses are updated in database

## Error Handling

- **Payment Failures**: Gracefully handle failed payments with detailed error messages
- **Network Issues**: Retry logic for API calls to Chapa
- **Database Errors**: Transaction rollback on database failures
- **Email Failures**: Log email sending failures without affecting payment flow

## Testing

### Sandbox Testing
Use Chapa's sandbox environment for testing:
- Test API keys are provided in the environment variables
- All transactions are simulated and no real money is transferred
- Full payment flow can be tested including webhooks

### Test Data
The test script creates:
- Test users (buyer and property host)
- Test property listings
- Test bookings with realistic amounts
- Test payments with different statuses

### Test Scenarios
1. Successful payment initiation
2. Payment verification
3. Failed payment handling
4. Booking status updates
5. Email notifications
6. API endpoint testing

## Security Considerations

1. **API Keys**: Store Chapa API keys securely in environment variables
2. **CSRF Protection**: Implement CSRF protection for payment endpoints
3. **Input Validation**: Validate all payment-related inputs
4. **Logging**: Log all payment activities for audit trails
5. **HTTPS**: Use HTTPS in production for secure communication

## Production Deployment

1. Set `DEBUG=False` in production
2. Configure proper email backend for notifications
3. Set up proper logging and monitoring
4. Use environment variables for all sensitive configuration
5. Configure proper database (PostgreSQL recommended)
6. Set up SSL/TLS certificates
7. Configure proper static file serving

## Monitoring and Logging

- Payment initiation attempts
- Payment verification results
- Failed payment reasons
- API response times
- Email delivery status
- Database transaction logs

## Support

For issues with the payment integration:
1. Check the Django logs for error messages
2. Verify environment variables are set correctly
3. Test with Chapa sandbox environment
4. Review payment status in Django admin
5. Check email delivery logs

## API Documentation

Complete API documentation is available at:
- Development: `http://localhost:8000/api/docs/`
- Admin Interface: `http://localhost:8000/admin/`

## License

This project is part of the ALX Software Engineering Program.
