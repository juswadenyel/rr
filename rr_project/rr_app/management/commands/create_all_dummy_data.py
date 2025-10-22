from django.core.management.base import BaseCommand
from django.core.management import call_command
from rr_app.models import Restaurant, Tags, Review, Customer
import time


class Command(BaseCommand):
    help = 'Create all dummy data for the restaurant app (restaurants, tags, customers, reviews)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurants',
            type=int,
            default=20,
            help='Number of restaurants to create (default: 20)'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=30,
            help='Number of tags to create (default: 30)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=150,
            help='Number of reviews to create (default: 150)'
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all existing data before creating new data'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output from each command'
        )

    def handle(self, *args, **options):
        restaurants_count = options['restaurants']
        tags_count = options['tags']
        reviews_count = options['reviews']
        clear_all = options['clear_all']
        verbose = options['verbose']

        start_time = time.time()

        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('CREATING COMPREHENSIVE DUMMY DATA'))
        self.stdout.write('='*60)

        # Step 1: Create Restaurants
        self.stdout.write('\n' + '='*30)
        self.stdout.write('STEP 1: Creating Restaurants')
        self.stdout.write('='*30)
        
        try:
            restaurant_args = ['create_dummy_restaurants', f'--count={restaurants_count}']
            if clear_all:
                restaurant_args.append('--clear')
            
            if verbose:
                call_command(*restaurant_args)
            else:
                call_command(*restaurant_args, stdout=open('nul', 'w') if verbose else None)
            
            restaurants_created = Restaurant.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {restaurants_created} restaurants in database')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating restaurants: {str(e)}')
            )
            return

        # Step 2: Create Tags and associate with restaurants
        self.stdout.write('\n' + '='*30)
        self.stdout.write('STEP 2: Creating Tags')
        self.stdout.write('='*30)
        
        try:
            tag_args = ['create_dummy_tags', f'--count={tags_count}', '--associate']
            if clear_all:
                tag_args.append('--clear')
            
            if verbose:
                call_command(*tag_args)
            else:
                call_command(*tag_args, stdout=open('nul', 'w') if not verbose else None)
            
            tags_created = Tags.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {tags_created} tags in database with restaurant associations')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating tags: {str(e)}')
            )

        # Step 3: Create Customers and Reviews
        self.stdout.write('\n' + '='*30)
        self.stdout.write('STEP 3: Creating Reviews')
        self.stdout.write('='*30)
        
        try:
            review_args = ['create_dummy_reviews', f'--count={reviews_count}', '--create-customers']
            if clear_all:
                review_args.append('--clear')
            
            if verbose:
                call_command(*review_args)
            else:
                call_command(*review_args, stdout=open('nul', 'w') if not verbose else None)
            
            reviews_created = Review.objects.count()
            customers_created = Customer.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {reviews_created} reviews in database')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ {customers_created} customers in database')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating reviews: {str(e)}')
            )

        # Final Summary
        end_time = time.time()
        duration = end_time - start_time

        self.stdout.write('\n' + '='*60)
        self.stdout.write('FINAL SUMMARY')
        self.stdout.write('='*60)
        
        total_restaurants = Restaurant.objects.count()
        total_tags = Tags.objects.count()
        total_reviews = Review.objects.count()
        total_customers = Customer.objects.count()
        
        # Calculate some statistics
        avg_reviews_per_restaurant = total_reviews / total_restaurants if total_restaurants > 0 else 0
        
        if total_reviews > 0:
            avg_rating = sum(float(review.rating) for review in Review.objects.all()) / total_reviews
        else:
            avg_rating = 0
        
        # Count tag associations
        total_associations = sum(tag.restaurants.count() for tag in Tags.objects.all())
        
        self.stdout.write(f"📊 DATABASE STATISTICS:")
        self.stdout.write(f"   • Restaurants: {total_restaurants}")
        self.stdout.write(f"   • Tags: {total_tags}")
        self.stdout.write(f"   • Reviews: {total_reviews}")
        self.stdout.write(f"   • Customers: {total_customers}")
        self.stdout.write(f"   • Tag-Restaurant associations: {total_associations}")
        self.stdout.write(f"")
        self.stdout.write(f"📈 CALCULATED METRICS:")
        self.stdout.write(f"   • Average reviews per restaurant: {avg_reviews_per_restaurant:.1f}")
        self.stdout.write(f"   • Average rating across all reviews: {avg_rating:.2f}/5.00")
        self.stdout.write(f"   • Average tags per restaurant: {total_associations/total_restaurants:.1f}")
        self.stdout.write(f"")
        self.stdout.write(f"⏱️  Total creation time: {duration:.2f} seconds")
        
        # Sample data preview
        self.stdout.write(f"\n📋 SAMPLE DATA PREVIEW:")
        
        # Show top 3 restaurants with their details
        for i, restaurant in enumerate(Restaurant.objects.all()[:3], 1):
            review_count = restaurant.reviews.count()
            tag_count = restaurant.tags.count()
            avg_restaurant_rating = 0
            
            if review_count > 0:
                avg_restaurant_rating = sum(float(review.rating) for review in restaurant.reviews.all()) / review_count
            
            self.stdout.write(f"   {i}. {restaurant.name}")
            self.stdout.write(f"      • Cuisine: {restaurant.cuisine_type}")
            self.stdout.write(f"      • Price: ${restaurant.price}")
            self.stdout.write(f"      • Reviews: {review_count} (avg: {avg_restaurant_rating:.1f}/5)")
            self.stdout.write(f"      • Tags: {tag_count}")
            if tag_count > 0:
                tags_list = [tag.tag for tag in restaurant.tags.all()[:3]]
                tags_display = ", ".join(tags_list)
                if tag_count > 3:
                    tags_display += f" (+{tag_count-3} more)"
                self.stdout.write(f"        Tags: {tags_display}")
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ ALL DUMMY DATA CREATION COMPLETED SUCCESSFULLY!'))
        self.stdout.write('='*60)
        
        self.stdout.write(f"\n🚀 Your restaurant app is now populated with comprehensive test data!")
        self.stdout.write(f"   You can now test all features including:")
        self.stdout.write(f"   • Restaurant listings with ratings and reviews")
        self.stdout.write(f"   • Tag-based filtering and categorization")
        self.stdout.write(f"   • Customer review system")
        self.stdout.write(f"   • Restaurant search and discovery features")