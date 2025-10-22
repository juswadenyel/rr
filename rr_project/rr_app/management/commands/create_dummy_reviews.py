from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rr_app.models import Review, Restaurant, Customer
from decimal import Decimal
import random
import datetime
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy review data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of reviews to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing reviews before creating new ones'
        )
        parser.add_argument(
            '--create-customers',
            action='store_true',
            help='Create dummy customers if none exist'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        create_customers = options['create_customers']

        if clear:
            Review.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing reviews.')
            )

        # Check if we have restaurants
        restaurants = list(Restaurant.objects.all())
        if not restaurants:
            self.stdout.write(
                self.style.ERROR('No restaurants found. Run create_dummy_restaurants first.')
            )
            return

        # Check if we have customers
        customers = list(Customer.objects.all())
        if not customers:
            if create_customers:
                self.create_dummy_customers()
                customers = list(Customer.objects.all())
            else:
                self.stdout.write(
                    self.style.ERROR(
                        'No customers found. Use --create-customers flag or create customers first.'
                    )
                )
                return

        # Review templates based on rating ranges
        review_templates = {
            # 5-star reviews
            (4.5, 5.0): [
                "Absolutely incredible dining experience! The service was impeccable and every dish was perfectly executed.",
                "Outstanding food and atmosphere. This place exceeded all our expectations. Highly recommend!",
                "Perfect evening out! The ambiance, food, and service were all exceptional. Will definitely be back.",
                "One of the best restaurants I've ever been to. The attention to detail is remarkable.",
                "Flawless experience from start to finish. The chef clearly knows what they're doing.",
                "Amazing! The flavors were incredible and the presentation was beautiful. Worth every penny.",
                "Exceptional service and delicious food. This place sets the standard for fine dining.",
                "Wonderful experience! The staff was attentive and the food was absolutely delicious.",
                "Perfect for a special occasion. Everything was excellent - food, service, and atmosphere.",
                "Outstanding! The menu is creative and every dish was perfectly prepared."
            ],
            # 4-star reviews
            (3.5, 4.4): [
                "Great food and good service. Really enjoyed our meal here. Would recommend.",
                "Solid choice for dinner. The atmosphere is nice and the food is well-prepared.",
                "Very good restaurant with tasty dishes and friendly staff. A bit pricey but worth it.",
                "Enjoyed our visit! The food was delicious and the service was good.",
                "Nice place with good food. The portions are generous and flavors are great.",
                "Good dining experience overall. The menu has nice variety and quality is consistent.",
                "Pleasant evening with good food and service. The restaurant has a nice ambiance.",
                "Really good food! The service was friendly and the atmosphere was comfortable.",
                "Great meal! The presentation was nice and flavors were well-balanced.",
                "Good restaurant with quality food. Staff was helpful and service was prompt."
            ],
            # 3-star reviews
            (2.5, 3.4): [
                "Decent food but nothing special. Service was okay. It's an average place.",
                "Food was alright, service could be better. Prices are reasonable though.",
                "It's okay. The food is decent but the service was a bit slow.",
                "Average experience. Food was fine but not memorable. Service was adequate.",
                "Not bad but not great either. The food is okay and portions are decent.",
                "Mediocre experience. Food was acceptable but nothing stood out.",
                "It's an okay place for a quick meal. Nothing special but not terrible either.",
                "Food was decent but took a while to arrive. Service could be more attentive.",
                "Average restaurant with okay food. Prices are fair for what you get.",
                "It's fine for what it is. Food is decent but atmosphere could be better."
            ],
            # 2-star reviews
            (1.5, 2.4): [
                "Disappointing experience. Food was below average and service was slow.",
                "Not impressed. The food lacked flavor and the service wasn't great.",
                "Food was mediocre and overpriced. Service was inattentive.",
                "Expected better. The food was bland and service was poor.",
                "Not worth the money. Food quality was disappointing.",
                "Poor experience overall. Food was cold when it arrived and service was slow.",
                "Underwhelming. The food didn't meet expectations and staff seemed disinterested.",
                "Disappointing meal. Food was average at best and service was lacking.",
                "Not a great experience. Food was overcooked and service was poor.",
                "Expected much more. Food was bland and service was unprofessional."
            ],
            # 1-star reviews
            (0.0, 1.4): [
                "Terrible experience. Food was awful and service was the worst I've ever had.",
                "Horrible! Food was cold, tasteless, and service was incredibly rude.",
                "Worst dining experience ever. Food was terrible and service was appalling.",
                "Absolutely awful. Food was inedible and staff was completely unprofessional.",
                "Never going back. Food was disgusting and service was terrible.",
                "Worst restaurant ever. Food was cold and tasteless, service was horrible.",
                "Terrible food and even worse service. Complete waste of money.",
                "Awful experience from start to finish. Food was gross and service was rude.",
                "Don't waste your time or money here. Everything was terrible.",
                "Horrible place. Food was inedible and service was the worst I've seen."
            ]
        }

        created_reviews = []
        
        for i in range(count):
            # Select random restaurant and customer
            restaurant = random.choice(restaurants)
            customer = random.choice(customers)
            
            # Generate rating with weighted distribution (more positive reviews)
            rating_weights = [0.05, 0.1, 0.15, 0.3, 0.4]  # 1-5 stars
            rating_choice = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
            
            # Add decimal precision
            rating = Decimal(f"{rating_choice}.{random.randint(0, 99):02d}")
            if rating > Decimal('5.00'):
                rating = Decimal('5.00')
            
            # Select appropriate comment based on rating
            comment = ""
            for (min_rating, max_rating), comments in review_templates.items():
                if min_rating <= float(rating) <= max_rating:
                    comment = random.choice(comments)
                    break
            
            # If no comment found, use a generic one
            if not comment:
                comment = "Had a meal here. Experience was okay overall."
            
            # Create review with random timestamp in the past 6 months
            days_ago = random.randint(1, 180)
            created_at = timezone.now() - datetime.timedelta(days=days_ago)
            
            review = Review.objects.create(
                customer=customer,
                restaurant=restaurant,
                rating=rating,
                comment=comment
            )
            
            # Set custom created_at (since auto_now_add prevents this normally)
            Review.objects.filter(id=review.id).update(created_at=created_at)
            
            created_reviews.append(review)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_reviews)} reviews'
            )
        )
        
        # Display summary statistics
        self.stdout.write('\n' + '='*50)
        self.stdout.write('REVIEW STATISTICS:')
        self.stdout.write('='*50)
        
        # Rating distribution
        for rating in [5, 4, 3, 2, 1]:
            count_in_range = len([r for r in created_reviews if int(float(r.rating)) == rating])
            percentage = (count_in_range / len(created_reviews)) * 100 if created_reviews else 0
            self.stdout.write(f"{rating} stars: {count_in_range} reviews ({percentage:.1f}%)")
        
        # Average rating
        if created_reviews:
            avg_rating = sum(float(r.rating) for r in created_reviews) / len(created_reviews)
            self.stdout.write(f"\nAverage rating: {avg_rating:.2f}")
        
        # Restaurant with most reviews
        from collections import Counter
        restaurant_counts = Counter(r.restaurant.name for r in created_reviews)
        if restaurant_counts:
            top_restaurant, top_count = restaurant_counts.most_common(1)[0]
            self.stdout.write(f"Most reviewed restaurant: {top_restaurant} ({top_count} reviews)")
        
        self.stdout.write(f"\nTotal reviews in database: {Review.objects.count()}")

    def create_dummy_customers(self):
        """Create dummy customers for reviews"""
        customer_data = [
            {"username": "foodlover123", "email": "foodlover123@example.com", "first_name": "Sarah", "last_name": "Johnson"},
            {"username": "dinerdave", "email": "dinerdave@example.com", "first_name": "Dave", "last_name": "Wilson"},
            {"username": "tastytina", "email": "tastytina@example.com", "first_name": "Tina", "last_name": "Chen"},
            {"username": "gourmetguy", "email": "gourmetguy@example.com", "first_name": "Michael", "last_name": "Brown"},
            {"username": "cuisinequeen", "email": "cuisinequeen@example.com", "first_name": "Emily", "last_name": "Davis"},
            {"username": "restaurantfan", "email": "restaurantfan@example.com", "first_name": "James", "last_name": "Miller"},
            {"username": "happyeater", "email": "happyeater@example.com", "first_name": "Lisa", "last_name": "Garcia"},
            {"username": "foodiefred", "email": "foodiefred@example.com", "first_name": "Fred", "last_name": "Taylor"},
            {"username": "deliciousdina", "email": "deliciousdina@example.com", "first_name": "Dina", "last_name": "Martinez"},
            {"username": "mealmaster", "email": "mealmaster@example.com", "first_name": "Alex", "last_name": "Anderson"},
            {"username": "chefeater", "email": "chefeater@example.com", "first_name": "Maria", "last_name": "Rodriguez"},
            {"username": "flavorfan", "email": "flavorfan@example.com", "first_name": "Robert", "last_name": "Lee"},
            {"username": "kitchenkid", "email": "kitchenkid@example.com", "first_name": "Jessica", "last_name": "White"},
            {"username": "platepal", "email": "platepal@example.com", "first_name": "Kevin", "last_name": "Thompson"},
            {"username": "menumaven", "email": "menumaven@example.com", "first_name": "Amanda", "last_name": "Clark"}
        ]
        
        created_customers = 0
        for data in customer_data:
            if not User.objects.filter(username=data["username"]).exists():
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    password="dummypass123"
                )
                Customer.objects.create(user=user)
                created_customers += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_customers} dummy customers')
        )