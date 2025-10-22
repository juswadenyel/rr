from django.core.management.base import BaseCommand
from rr_app.models import Restaurant, Tags, Review, Customer, User, Reservation
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear all restaurant-related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data'
        )
        parser.add_argument(
            '--keep-users',
            action='store_true',
            help='Keep user accounts (only delete restaurant, tag, review data)'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        keep_users = options['keep_users']

        if not confirm:
            self.stdout.write(
                self.style.ERROR(
                    'This command will delete ALL restaurant-related data!\n'
                    'Use --confirm flag if you really want to proceed.\n'
                    'Example: python manage.py clear_all_data --confirm'
                )
            )
            return

        self.stdout.write('='*50)
        self.stdout.write(self.style.WARNING('CLEARING ALL DATA'))
        self.stdout.write('='*50)

        # Count existing data
        restaurants_count = Restaurant.objects.count()
        tags_count = Tags.objects.count()
        reviews_count = Review.objects.count()
        reservations_count = Reservation.objects.count()
        customers_count = Customer.objects.count()

        self.stdout.write(f"Data to be deleted:")
        self.stdout.write(f"  • Restaurants: {restaurants_count}")
        self.stdout.write(f"  • Tags: {tags_count}")
        self.stdout.write(f"  • Reviews: {reviews_count}")
        self.stdout.write(f"  • Reservations: {reservations_count}")

        if not keep_users:
            self.stdout.write(f"  • Customers: {customers_count}")

        # Delete data in proper order (foreign key constraints)
        try:
            # Reviews depend on restaurants and customers
            Review.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {reviews_count} reviews"))

            # Reservations depend on restaurants and users
            Reservation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {reservations_count} reservations"))

            # Tags have many-to-many with restaurants
            Tags.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {tags_count} tags"))

            # Restaurants
            Restaurant.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {restaurants_count} restaurants"))

            # Customers and Users (if not keeping)
            if not keep_users:
                Customer.objects.all().delete()
                # Delete dummy users (be careful not to delete admin users)
                dummy_users = User.objects.filter(
                    email__icontains='example.com'
                ).exclude(
                    is_superuser=True
                ).exclude(
                    is_staff=True
                )
                dummy_count = dummy_users.count()
                dummy_users.delete()
                self.stdout.write(self.style.SUCCESS(f"✓ Deleted {customers_count} customers and {dummy_count} dummy users"))
            else:
                self.stdout.write(self.style.WARNING("⚠ Kept user accounts as requested"))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error during deletion: {str(e)}")
            )
            return

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✓ ALL DATA CLEARED SUCCESSFULLY'))
        self.stdout.write('='*50)

        # Final counts
        final_restaurants = Restaurant.objects.count()
        final_tags = Tags.objects.count()
        final_reviews = Review.objects.count()
        final_reservations = Reservation.objects.count()
        final_customers = Customer.objects.count()

        self.stdout.write(f"\nRemaining data counts:")
        self.stdout.write(f"  • Restaurants: {final_restaurants}")
        self.stdout.write(f"  • Tags: {final_tags}")
        self.stdout.write(f"  • Reviews: {final_reviews}")
        self.stdout.write(f"  • Reservations: {final_reservations}")
        self.stdout.write(f"  • Customers: {final_customers}")

        if keep_users:
            self.stdout.write(f"\n💡 User accounts were preserved.")
            self.stdout.write(f"   You can now create new dummy data without losing login credentials.")
        else:
            self.stdout.write(f"\n💡 The database is now clean.")
            self.stdout.write(f"   You can create fresh dummy data using: python manage.py create_all_dummy_data")