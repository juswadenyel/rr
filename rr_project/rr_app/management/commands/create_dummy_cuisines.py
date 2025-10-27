from django.core.management.base import BaseCommand
from rr_app.models import Cuisine, Restaurant
import random


class Command(BaseCommand):
    help = 'Create dummy cuisine data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cuisines before creating new ones'
        )
        parser.add_argument(
            '--associate',
            action='store_true',
            help='Associate cuisines with existing restaurants'
        )

    def handle(self, *args, **options):
        clear = options['clear']
        associate = options['associate']

        if clear:
            Cuisine.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing cuisines.')
            )

        # Comprehensive list of world cuisines
        cuisines = [
            # European Cuisines
            'Italian', 'French', 'Spanish', 'Greek', 'German', 'British', 'Irish',
            'Portuguese', 'Dutch', 'Belgian', 'Swiss', 'Austrian', 'Scandinavian',
            'Russian', 'Eastern European', 'Mediterranean',
            
            # Asian Cuisines
            'Chinese', 'Japanese', 'Korean', 'Thai', 'Vietnamese', 'Indian',
            'Pakistani', 'Bangladeshi', 'Sri Lankan', 'Indonesian', 'Malaysian',
            'Filipino', 'Singaporean', 'Mongolian', 'Nepalese', 'Tibetan',
            'Burmese', 'Cambodian', 'Laotian',
            
            # Middle Eastern & North African
            'Middle Eastern', 'Turkish', 'Lebanese', 'Persian', 'Israeli',
            'Moroccan', 'Egyptian', 'Ethiopian', 'Tunisian', 'Jordanian',
            'Syrian', 'Kurdish', 'Armenian',
            
            # Americas
            'Mexican', 'American', 'Tex-Mex', 'Californian', 'Southern American',
            'Brazilian', 'Argentinian', 'Peruvian', 'Colombian', 'Venezuelan',
            'Chilean', 'Ecuadorian', 'Bolivian', 'Cuban', 'Puerto Rican',
            'Jamaican', 'Caribbean', 'Central American',
            
            # African
            'South African', 'Nigerian', 'Ghanaian', 'Kenyan', 'Senegalese',
            'Zimbabwean', 'Tanzanian', 'Ugandan',
            
            # Oceania
            'Australian', 'New Zealand', 'Pacific Islander', 'Hawaiian',
            
            # Fusion & Modern
            'Asian Fusion', 'Modern American', 'Contemporary', 'International',
            'Fusion', 'New World', 'Global', 'Eclectic',
            
            # Dietary & Style Categories
            'Vegetarian', 'Vegan', 'Raw Food', 'Organic', 'Farm-to-Table',
            'Gluten-Free', 'Healthy', 'Comfort Food', 'Street Food',
            'Fast Food', 'Fine Dining', 'Casual Dining',
            
            # Specific Food Types
            'Seafood', 'Steakhouse', 'BBQ', 'Pizza', 'Burgers', 'Sandwiches',
            'Salads', 'Soup', 'Noodles', 'Dumplings', 'Tapas', 'Sushi',
            'Ramen', 'Dim Sum', 'Hot Pot', 'Fondue', 'Buffet'
        ]

        created_cuisines = []
        
        # Create all cuisines
        for cuisine_name in cuisines:
            # Check if cuisine already exists
            if not Cuisine.objects.filter(name=cuisine_name).exists():
                cuisine = Cuisine.objects.create(name=cuisine_name)
                created_cuisines.append(cuisine)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_cuisines)} cuisines'
            )
        )

        # Associate cuisines with restaurants if requested
        if associate:
            restaurants = Restaurant.objects.all()
            if restaurants.exists():
                total_associations = 0
                
                for restaurant in restaurants:
                    # Each restaurant gets 1-3 random cuisines
                    num_cuisines = random.randint(1, 3)
                    available_cuisines = list(Cuisine.objects.all())
                    selected_cuisines = random.sample(
                        available_cuisines, 
                        min(num_cuisines, len(available_cuisines))
                    )
                    
                    # Associate cuisines with restaurant
                    for cuisine in selected_cuisines:
                        cuisine.restaurant.add(restaurant)
                        total_associations += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {total_associations} cuisine-restaurant associations'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'No restaurants found. Run create_dummy_restaurants first to associate.'
                    )
                )
        
        # Display summary organized by regions
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY OF CREATED CUISINES:')
        self.stdout.write('='*50)
        
        # Organize cuisines by regions for better display
        regions = {
            'European': ['Italian', 'French', 'Spanish', 'Greek', 'German', 'British', 'Irish', 'Portuguese', 'Dutch', 'Belgian', 'Swiss', 'Austrian', 'Scandinavian', 'Russian', 'Eastern European', 'Mediterranean'],
            'Asian': ['Chinese', 'Japanese', 'Korean', 'Thai', 'Vietnamese', 'Indian', 'Pakistani', 'Bangladeshi', 'Sri Lankan', 'Indonesian', 'Malaysian', 'Filipino', 'Singaporean', 'Mongolian', 'Nepalese', 'Tibetan', 'Burmese', 'Cambodian', 'Laotian'],
            'Middle Eastern & African': ['Middle Eastern', 'Turkish', 'Lebanese', 'Persian', 'Israeli', 'Moroccan', 'Egyptian', 'Ethiopian', 'Tunisian', 'Jordanian', 'Syrian', 'Kurdish', 'Armenian', 'South African', 'Nigerian', 'Ghanaian', 'Kenyan', 'Senegalese'],
            'Americas': ['Mexican', 'American', 'Tex-Mex', 'Brazilian', 'Argentinian', 'Peruvian', 'Colombian', 'Cuban', 'Caribbean', 'Southern American', 'Californian'],
            'Modern & Fusion': ['Asian Fusion', 'Modern American', 'Contemporary', 'International', 'Fusion', 'Farm-to-Table', 'Fine Dining']
        }
        
        for region, region_cuisines in regions.items():
            created_in_region = [c for c in created_cuisines if c.name in region_cuisines]
            if created_in_region:
                self.stdout.write(f"\n{region} ({len(created_in_region)} cuisines):")
                for cuisine in created_in_region[:8]:  # Show first 8 per region
                    restaurant_count = cuisine.restaurant.count()
                    self.stdout.write(f"  • {cuisine.name} ({restaurant_count} restaurants)")
                
                if len(created_in_region) > 8:
                    self.stdout.write(f"  ... and {len(created_in_region) - 8} more")
        
        # Show some remaining cuisines not in regions
        other_cuisines = [c for c in created_cuisines if not any(c.name in region_list for region_list in regions.values())]
        if other_cuisines:
            self.stdout.write(f"\nSpecialty & Other ({len(other_cuisines)} cuisines):")
            for cuisine in other_cuisines[:8]:
                restaurant_count = cuisine.restaurant.count()
                self.stdout.write(f"  • {cuisine.name} ({restaurant_count} restaurants)")
            
            if len(other_cuisines) > 8:
                self.stdout.write(f"  ... and {len(other_cuisines) - 8} more")
        
        self.stdout.write(f"\nTotal cuisines in database: {Cuisine.objects.count()}")
        
        if associate and restaurants.exists():
            # Show some examples of restaurant-cuisine associations
            self.stdout.write(f"\nSample Restaurant-Cuisine Associations:")
            for restaurant in restaurants[:3]:
                restaurant_cuisines = restaurant.cuisines.all()
                if restaurant_cuisines:
                    cuisine_names = [c.name for c in restaurant_cuisines]
                    self.stdout.write(f"  • {restaurant.name}: {', '.join(cuisine_names)}")