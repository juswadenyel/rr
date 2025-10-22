from django.core.management.base import BaseCommand
from rr_app.models import Restaurant, Tags, Review, Customer, Reservation
from django.contrib.auth import get_user_model
from collections import Counter
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Show comprehensive summary of all restaurant data in the database'

    def handle(self, *args, **options):
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('RESTAURANT APP DATA SUMMARY'))
        self.stdout.write('='*70)

        # Get all data counts
        restaurants_count = Restaurant.objects.count()
        tags_count = Tags.objects.count()
        reviews_count = Review.objects.count()
        customers_count = Customer.objects.count()
        reservations_count = Reservation.objects.count()
        users_count = User.objects.count()

        # Basic statistics
        self.stdout.write(f"\n📊 BASIC STATISTICS:")
        self.stdout.write(f"   • Restaurants: {restaurants_count}")
        self.stdout.write(f"   • Tags: {tags_count}")
        self.stdout.write(f"   • Reviews: {reviews_count}")
        self.stdout.write(f"   • Customers: {customers_count}")
        self.stdout.write(f"   • Reservations: {reservations_count}")
        self.stdout.write(f"   • Total Users: {users_count}")

        if restaurants_count > 0:
            # Restaurant statistics
            self.stdout.write(f"\n🏪 RESTAURANT DETAILS:")
            
            # Cuisine distribution
            cuisines = Counter(r.cuisine_type for r in Restaurant.objects.all())
            self.stdout.write(f"   Cuisine Types ({len(cuisines)} different):")
            for cuisine, count in cuisines.most_common(5):
                self.stdout.write(f"     • {cuisine}: {count} restaurants")
            if len(cuisines) > 5:
                self.stdout.write(f"     ... and {len(cuisines) - 5} more cuisines")
            
            # Price ranges
            prices = [float(r.price) for r in Restaurant.objects.all()]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            self.stdout.write(f"   Price Range: ${min_price:.2f} - ${max_price:.2f} (avg: ${avg_price:.2f})")

        if tags_count > 0:
            # Tag statistics
            self.stdout.write(f"\n🏷️  TAG STATISTICS:")
            total_associations = sum(tag.restaurants.count() for tag in Tags.objects.all())
            avg_tags_per_restaurant = total_associations / restaurants_count if restaurants_count > 0 else 0
            self.stdout.write(f"   • Total tag-restaurant associations: {total_associations}")
            self.stdout.write(f"   • Average tags per restaurant: {avg_tags_per_restaurant:.1f}")
            
            # Most popular tags
            popular_tags = [(tag.tag, tag.restaurants.count()) for tag in Tags.objects.all()]
            popular_tags.sort(key=lambda x: x[1], reverse=True)
            self.stdout.write(f"   Most Popular Tags:")
            for tag_name, count in popular_tags[:5]:
                self.stdout.write(f"     • {tag_name}: {count} restaurants")

        if reviews_count > 0:
            # Review statistics
            self.stdout.write(f"\n⭐ REVIEW STATISTICS:")
            ratings = [float(r.rating) for r in Review.objects.all()]
            avg_rating = sum(ratings) / len(ratings)
            self.stdout.write(f"   • Average rating: {avg_rating:.2f}/5.00")
            
            # Rating distribution
            rating_dist = Counter(int(float(r.rating)) for r in Review.objects.all())
            self.stdout.write(f"   Rating Distribution:")
            for star in [5, 4, 3, 2, 1]:
                count = rating_dist.get(star, 0)
                percentage = (count / reviews_count) * 100
                self.stdout.write(f"     • {star} stars: {count} reviews ({percentage:.1f}%)")
            
            # Most reviewed restaurants
            restaurant_reviews = Counter(r.restaurant.name for r in Review.objects.all())
            self.stdout.write(f"   Most Reviewed Restaurants:")
            for restaurant_name, count in restaurant_reviews.most_common(3):
                self.stdout.write(f"     • {restaurant_name}: {count} reviews")

        if customers_count > 0:
            # Customer statistics
            self.stdout.write(f"\n👥 CUSTOMER STATISTICS:")
            # Reviews per customer
            customer_reviews = Counter(r.customer.id for r in Review.objects.all() if r.customer)
            if customer_reviews:
                avg_reviews_per_customer = sum(customer_reviews.values()) / len(customer_reviews)
                most_active_customer_id = customer_reviews.most_common(1)[0][0]
                most_active_customer = Customer.objects.get(id=most_active_customer_id)
                most_active_reviews = customer_reviews.most_common(1)[0][1]
                
                self.stdout.write(f"   • Average reviews per customer: {avg_reviews_per_customer:.1f}")
                self.stdout.write(f"   • Most active customer: {most_active_customer.user.get_full_name() or most_active_customer.user.username} ({most_active_reviews} reviews)")

        # Sample data showcase
        if restaurants_count > 0:
            self.stdout.write(f"\n🎯 SAMPLE RESTAURANT SHOWCASE:")
            sample_restaurants = Restaurant.objects.all()[:3]
            
            for i, restaurant in enumerate(sample_restaurants, 1):
                reviews = restaurant.reviews.all()
                tags = restaurant.tags.all()
                avg_restaurant_rating = 0
                
                if reviews:
                    avg_restaurant_rating = sum(float(r.rating) for r in reviews) / len(reviews)
                
                self.stdout.write(f"   {i}. {restaurant.name}")
                self.stdout.write(f"      • Cuisine: {restaurant.cuisine_type} | Price: ${restaurant.price}")
                self.stdout.write(f"      • Location: {restaurant.address}")
                self.stdout.write(f"      • Reviews: {len(reviews)} (avg: {avg_restaurant_rating:.1f}⭐)")
                
                if tags:
                    tag_list = [tag.tag for tag in tags[:4]]
                    tag_display = ", ".join(tag_list)
                    if len(tags) > 4:
                        tag_display += f" (+{len(tags)-4} more)"
                    self.stdout.write(f"      • Tags: {tag_display}")
                
                if reviews:
                    latest_review = reviews.order_by('-created_at').first()
                    self.stdout.write(f"      • Latest Review: \"{latest_review.comment[:60]}{'...' if len(latest_review.comment) > 60 else ''}\" ({float(latest_review.rating)}⭐)")
                self.stdout.write("")

        # Data quality insights
        self.stdout.write(f"\n📈 DATA QUALITY INSIGHTS:")
        if restaurants_count > 0:
            # Restaurants with no reviews
            restaurants_no_reviews = Restaurant.objects.filter(reviews__isnull=True).count()
            self.stdout.write(f"   • Restaurants without reviews: {restaurants_no_reviews} ({(restaurants_no_reviews/restaurants_count)*100:.1f}%)")
            
            # Restaurants with no tags
            restaurants_no_tags = sum(1 for r in Restaurant.objects.all() if r.tags.count() == 0)
            self.stdout.write(f"   • Restaurants without tags: {restaurants_no_tags} ({(restaurants_no_tags/restaurants_count)*100:.1f}%)")

        # Usage recommendations
        self.stdout.write(f"\n💡 USAGE RECOMMENDATIONS:")
        if restaurants_count == 0:
            self.stdout.write(f"   • Run 'python manage.py create_dummy_restaurants' to create restaurant data")
        if tags_count == 0:
            self.stdout.write(f"   • Run 'python manage.py create_dummy_tags --associate' to create tags")
        if reviews_count == 0:
            self.stdout.write(f"   • Run 'python manage.py create_dummy_reviews --create-customers' to create reviews")
        if restaurants_count > 0 and reviews_count > 0 and tags_count > 0:
            self.stdout.write(f"   • Your database is well-populated for testing!")
            self.stdout.write(f"   • You can test search, filtering, reviews, and booking features")
            self.stdout.write(f"   • Consider running the development server to see the UI")

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('DATA SUMMARY COMPLETE'))
        self.stdout.write('='*70)