from django.core.management.base import BaseCommand
from django.db import transaction
from rr_app.models import Restaurant, Review, Reservation
from collections import defaultdict
import re


class Command(BaseCommand):
    help = 'Remove duplicate restaurants from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--criteria',
            type=str,
            choices=['name', 'name_address', 'name_cuisine', 'all'],
            default='name',
            help='Criteria for detecting duplicates (default: name)'
        )
        parser.add_argument(
            '--auto-confirm',
            action='store_true',
            help='Skip confirmation prompts'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        criteria = options['criteria']
        auto_confirm = options['auto_confirm']

        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('RESTAURANT DEDUPLICATION TOOL'))
        self.stdout.write('='*70)

        # Get all restaurants
        restaurants = Restaurant.objects.all().order_by('created_at')
        initial_count = restaurants.count()

        if initial_count == 0:
            self.stdout.write(self.style.WARNING('No restaurants found in the database.'))
            return

        self.stdout.write(f"\nAnalyzing {initial_count} restaurants for duplicates...")
        self.stdout.write(f"Using criteria: {criteria}")

        # Find duplicates based on the selected criteria
        duplicates = self.find_duplicates(restaurants, criteria)

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('\n✅ No duplicates found! Your database is clean.'))
            return

        total_duplicates = sum(len(group) - 1 for group in duplicates.values())
        self.stdout.write(f"\n🔍 Found {len(duplicates)} duplicate groups with {total_duplicates} restaurants to remove:")

        # Display duplicates
        for key, group in duplicates.items():
            self.stdout.write(f"\n📍 Duplicate Group: {key}")
            self.stdout.write(f"   Found {len(group)} restaurants (keeping 1, removing {len(group) - 1}):")
            
            # Sort by creation date to keep the oldest
            group_sorted = sorted(group, key=lambda x: x.created_at)
            keeper = group_sorted[0]
            to_remove = group_sorted[1:]

            self.stdout.write(f"   ✅ KEEP:   {keeper.name} (ID: {keeper.id}) - Created: {keeper.created_at.strftime('%Y-%m-%d %H:%M')}")
            for restaurant in to_remove:
                reviews_count = restaurant.reviews.count()
                reservations_count = restaurant.reservations.count()
                self.stdout.write(f"   ❌ REMOVE: {restaurant.name} (ID: {restaurant.id}) - Created: {restaurant.created_at.strftime('%Y-%m-%d %H:%M')}")
                if reviews_count > 0 or reservations_count > 0:
                    self.stdout.write(f"              ⚠️  Has {reviews_count} reviews and {reservations_count} reservations")

        # Show summary
        self.stdout.write(f"\n📊 SUMMARY:")
        self.stdout.write(f"   • Total restaurants: {initial_count}")
        self.stdout.write(f"   • Duplicate groups: {len(duplicates)}")
        self.stdout.write(f"   • Restaurants to remove: {total_duplicates}")
        self.stdout.write(f"   • Restaurants after cleanup: {initial_count - total_duplicates}")

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE: No changes were made to the database.'))
            self.stdout.write('Run without --dry-run to actually remove duplicates.')
            return

        # Confirm deletion
        if not auto_confirm:
            self.stdout.write(f"\n⚠️  WARNING: This will permanently delete {total_duplicates} restaurants and their associated data.")
            confirm = input("Do you want to proceed? (yes/no): ").lower().strip()
            if confirm not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Perform deletion
        self.stdout.write('\n🗑️  Removing duplicate restaurants...')
        
        removed_count = 0
        preserved_reviews = 0
        preserved_reservations = 0

        with transaction.atomic():
            for key, group in duplicates.items():
                group_sorted = sorted(group, key=lambda x: x.created_at)
                keeper = group_sorted[0]
                to_remove = group_sorted[1:]

                # Before removing, migrate reviews and reservations to the keeper
                for restaurant in to_remove:
                    # Migrate reviews
                    reviews = list(restaurant.reviews.all())
                    for review in reviews:
                        review.restaurant = keeper
                        review.save()
                        preserved_reviews += 1

                    # Migrate reservations
                    reservations = list(restaurant.reservations.all())
                    for reservation in reservations:
                        reservation.restaurant = keeper
                        reservation.save()
                        preserved_reservations += 1

                    # Delete the duplicate restaurant
                    restaurant_name = restaurant.name
                    restaurant.delete()
                    removed_count += 1
                    self.stdout.write(f"   ✅ Removed: {restaurant_name}")

        # Final summary
        final_count = Restaurant.objects.count()
        self.stdout.write(f"\n✅ DEDUPLICATION COMPLETE!")
        self.stdout.write(f"   • Restaurants removed: {removed_count}")
        self.stdout.write(f"   • Reviews preserved: {preserved_reviews}")
        self.stdout.write(f"   • Reservations preserved: {preserved_reservations}")
        self.stdout.write(f"   • Final restaurant count: {final_count}")

        if preserved_reviews > 0 or preserved_reservations > 0:
            self.stdout.write(f"   • All associated data was migrated to the kept restaurants")

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('DEDUPLICATION COMPLETE'))
        self.stdout.write('='*70)

    def find_duplicates(self, restaurants, criteria):
        """Find duplicate restaurants based on the specified criteria"""
        groups = defaultdict(list)

        for restaurant in restaurants:
            if criteria == 'name':
                # Remove numeric suffixes like " 1", " 2" etc.
                clean_name = re.sub(r'\s+\d+$', '', restaurant.name.strip())
                key = clean_name.lower()
            elif criteria == 'name_address':
                clean_name = re.sub(r'\s+\d+$', '', restaurant.name.strip())
                key = (clean_name.lower(), restaurant.address.lower())
            elif criteria == 'name_cuisine':
                clean_name = re.sub(r'\s+\d+$', '', restaurant.name.strip())
                key = (clean_name.lower(), restaurant.cuisine_type.lower())
            elif criteria == 'all':
                clean_name = re.sub(r'\s+\d+$', '', restaurant.name.strip())
                key = (clean_name.lower(), restaurant.address.lower(), restaurant.cuisine_type.lower())
            
            groups[key].append(restaurant)

        # Filter to only include groups with duplicates
        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        return duplicates

    def normalize_restaurant_name(self, name):
        """Normalize restaurant name by removing numeric suffixes and extra spaces"""
        # Remove numeric suffixes like " 1", " 2", etc.
        normalized = re.sub(r'\s+\d+$', '', name.strip())
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized