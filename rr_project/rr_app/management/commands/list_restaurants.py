from django.core.management.base import BaseCommand
from rr_app.models import Restaurant


class Command(BaseCommand):
    help = 'List all restaurants in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information for each restaurant'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        restaurants = Restaurant.objects.all().order_by('name')
        
        if not restaurants.exists():
            self.stdout.write(
                self.style.WARNING('No restaurants found in the database.')
            )
            return
        
        self.stdout.write(f"\nFound {restaurants.count()} restaurants:")
        self.stdout.write('='*60)
        
        for i, restaurant in enumerate(restaurants, 1):
            if detailed:
                self.stdout.write(f"\n{i}. {restaurant.name}")
                self.stdout.write(f"   Cuisine: {restaurant.cuisine_type}")
                self.stdout.write(f"   Price: ${restaurant.price}")
                self.stdout.write(f"   Address: {restaurant.address}")
                self.stdout.write(f"   Email: {restaurant.email}")
                self.stdout.write(f"   Phone: {restaurant.phone_number}")
                self.stdout.write(f"   Description: {restaurant.description[:100]}...")
                self.stdout.write('-'*60)
            else:
                self.stdout.write(
                    f"{i:2d}. {restaurant.name:<25} | {restaurant.cuisine_type:<15} | ${restaurant.price:>7}"
                )