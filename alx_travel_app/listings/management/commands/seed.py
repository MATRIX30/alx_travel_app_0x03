from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        if not User.objects.exists():
            user = User.objects.create_user(username='hostuser', password='password')
        else:
            user = User.objects.first()

        sample_listings = [
            {
                'name': 'Cozy Apartment',
                'description': 'A nice and cozy apartment in the city center.',
                'location': 'Nairobi',
                'pricepernight': 50.00,
            },
            {
                'name': 'Beach House',
                'description': 'Enjoy the sea breeze in this beautiful beach house.',
                'location': 'Mombasa',
                'pricepernight': 120.00,
            },
            {
                'name': 'Mountain Cabin',
                'description': 'A peaceful retreat in the mountains.',
                'location': 'Mt. Kenya',
                'pricepernight': 80.00,
            },
        ]

        for data in sample_listings:
            Listing.objects.get_or_create(
                host=user,
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'location': data['location'],
                    'pricepernight': data['pricepernight'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Sample listings seeded.'))