from django.core.management.base import BaseCommand
from rr_app.models import Tags, Restaurant
import random


class Command(BaseCommand):
    help = 'Create dummy tag data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of tags to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing tags before creating new ones'
        )
        parser.add_argument(
            '--associate',
            action='store_true',
            help='Associate tags with existing restaurants'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        associate = options['associate']

        if clear:
            Tags.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing tags.')
            )

        # Restaurant tags organized by category
        tag_categories = {
            'Atmosphere': [
                'Romantic', 'Family-Friendly', 'Cozy', 'Elegant', 'Casual',
                'Trendy', 'Historic', 'Modern', 'Intimate', 'Lively',
                'Quiet', 'Vibrant', 'Sophisticated', 'Rustic', 'Contemporary'
            ],
            'Features': [
                'Outdoor Seating', 'Live Music', 'Wine Bar', 'Craft Cocktails',
                'Open Kitchen', 'Private Dining', 'Rooftop', 'Waterfront',
                'Pet-Friendly', 'WiFi Available', 'Parking Available',
                'Wheelchair Accessible', 'Fireplace', 'Garden', 'Terrace'
            ],
            'Dining Style': [
                'Fine Dining', 'Buffet', 'Tapas', 'Brunch', 'Late Night',
                'Quick Service', 'Farm-to-Table', 'Organic', 'Vegan Options',
                'Gluten-Free Options', 'Halal', 'Kosher', 'Fresh Seafood',
                'Steakhouse', 'Sushi Bar'
            ],
            'Special Occasions': [
                'Date Night', 'Business Lunch', 'Birthday Parties',
                'Anniversary Dinner', 'Group Events', 'Wedding Reception',
                'Happy Hour', 'Sunday Brunch', 'Holiday Dining',
                'Celebration Dining'
            ],
            'Price & Value': [
                'Great Value', 'Affordable', 'Premium', 'All-You-Can-Eat',
                'Large Portions', 'Student Discounts', 'Senior Discounts',
                'Early Bird Specials', 'Prix Fixe Menu', 'Lunch Deals'
            ]
        }

        # Flatten all tags into a single list
        all_tags = []
        for category, tags in tag_categories.items():
            all_tags.extend(tags)

        # Shuffle for random selection
        random.shuffle(all_tags)

        created_tags = []
        
        # Create the specified number of tags
        for i in range(min(count, len(all_tags))):
            tag_name = all_tags[i]
            
            # Check if tag already exists
            if not Tags.objects.filter(tag=tag_name).exists():
                tag = Tags.objects.create(tag=tag_name)
                created_tags.append(tag)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_tags)} tags'
            )
        )

        # Associate tags with restaurants if requested
        if associate:
            restaurants = Restaurant.objects.all()
            if restaurants.exists():
                total_associations = 0
                
                for restaurant in restaurants:
                    # Each restaurant gets 2-5 random tags
                    num_tags = random.randint(2, 5)
                    available_tags = list(Tags.objects.all())
                    selected_tags = random.sample(
                        available_tags, 
                        min(num_tags, len(available_tags))
                    )
                    
                    # Associate tags with restaurant
                    for tag in selected_tags:
                        tag.restaurants.add(restaurant)
                        total_associations += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {total_associations} tag-restaurant associations'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'No restaurants found. Run create_dummy_restaurants first.'
                    )
                )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY OF CREATED TAGS:')
        self.stdout.write('='*50)
        
        # Group tags by category for display
        for category, category_tags in tag_categories.items():
            created_in_category = [tag for tag in created_tags if tag.tag in category_tags]
            if created_in_category:
                self.stdout.write(f"\n{category}:")
                for tag in created_in_category[:5]:  # Show first 5 per category
                    restaurant_count = tag.restaurants.count()
                    self.stdout.write(f"  • {tag.tag} ({restaurant_count} restaurants)")
                
                if len(created_in_category) > 5:
                    self.stdout.write(f"  ... and {len(created_in_category) - 5} more")
        
        self.stdout.write(f"\nTotal tags in database: {Tags.objects.count()}")