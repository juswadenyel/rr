from django.core.management.base import BaseCommand
from rr_app.models import Restaurant
from datetime import time
import random


class Command(BaseCommand):
    help = 'Add dummy opening and closing times to restaurants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing hours for restaurants that already have them',
        )

    def handle(self, *args, **options):
        restaurants = Restaurant.objects.all()
        
        if not restaurants.exists():
            self.stdout.write(
                self.style.WARNING('No restaurants found in database.')
            )
            return

        # Common restaurant opening/closing time patterns
        opening_times = [
            time(8, 0),   # 8:00 AM - Breakfast places
            time(9, 0),   # 9:00 AM - Cafes
            time(10, 0),  # 10:00 AM - Brunch spots
            time(11, 0),  # 11:00 AM - Lunch places
            time(11, 30), # 11:30 AM - Lunch places
            time(12, 0),  # 12:00 PM - Lunch only
            time(17, 0),  # 5:00 PM - Dinner only
            time(17, 30), # 5:30 PM - Dinner places
            time(18, 0),  # 6:00 PM - Dinner places
        ]
        
        closing_times = [
            time(14, 0),  # 2:00 PM - Lunch only
            time(15, 0),  # 3:00 PM - Cafes
            time(20, 0),  # 8:00 PM - Family restaurants
            time(21, 0),  # 9:00 PM - Casual dining
            time(21, 30), # 9:30 PM - Restaurants
            time(22, 0),  # 10:00 PM - Standard restaurants
            time(22, 30), # 10:30 PM - Restaurants
            time(23, 0),  # 11:00 PM - Late night dining
            time(23, 30), # 11:30 PM - Late night
            time(0, 0),   # 12:00 AM - Very late night
            time(1, 0),   # 1:00 AM - Bars & late night eateries
            time(2, 0),   # 2:00 AM - Late night spots
        ]

        updated_count = 0
        skipped_count = 0
        
        for restaurant in restaurants:
            # Skip if restaurant already has hours and force is not specified
            if restaurant.opening_time and restaurant.closing_time and not options['force']:
                skipped_count += 1
                continue
            
            # Randomly assign opening and closing times
            opening_time = random.choice(opening_times)
            closing_time = random.choice(closing_times)
            
            # Ensure closing time makes sense relative to opening time
            # If it's a lunch-only place (closes at 2-3 PM), ensure early opening
            if closing_time.hour <= 15:
                opening_time = random.choice([time(8, 0), time(9, 0), time(10, 0), time(11, 0), time(11, 30)])
            
            # If it's a dinner-only place (opens after 5 PM), ensure late closing
            elif opening_time.hour >= 17:
                closing_time = random.choice([time(21, 0), time(21, 30), time(22, 0), time(22, 30), time(23, 0), time(23, 30), time(0, 0), time(1, 0), time(2, 0)])
            
            restaurant.opening_time = opening_time
            restaurant.closing_time = closing_time
            restaurant.save()
            
            updated_count += 1
            
            # Display what we set
            opening_str = opening_time.strftime("%I:%M %p")
            closing_str = closing_time.strftime("%I:%M %p")
            
            self.stdout.write(
                f"  • {restaurant.name}: {opening_str} - {closing_str}"
            )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully updated {updated_count} restaurants with dummy hours!'
            )
        )
        
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Skipped {skipped_count} restaurants that already have hours.'
                )
            )
            self.stdout.write(
                f'   Use --force flag to overwrite existing hours.'
            )
            
        self.stdout.write('='*60)