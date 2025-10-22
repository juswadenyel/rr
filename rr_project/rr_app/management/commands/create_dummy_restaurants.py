from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from rr_app.models import Restaurant
import random
from decimal import Decimal
import os
from django.conf import settings

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Command(BaseCommand):
    help = 'Create dummy restaurant data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of restaurants to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing restaurants before creating new ones'
        )
        parser.add_argument(
            '--with-images',
            action='store_true',
            help='Download placeholder images for restaurants (requires internet)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        with_images = options['with_images']

        if clear:
            Restaurant.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing restaurants.')
            )

        # Restaurant names
        restaurant_names = [
            "The Golden Fork", "Bella Vista", "Ocean Breeze", "Urban Spice",
            "The Rustic Table", "Moonlight Bistro", "Garden Terrace", "Fire & Stone",
            "The Blue Elephant", "Harvest Kitchen", "Crimson Rose", "Sunset Grill",
            "The Copper Pot", "Emerald Bay", "Mountain View", "The Silver Spoon",
            "Coastal Catch", "The Wild Olive", "Ruby Tuesday", "Sapphire Lounge",
            "The Green Garden", "Midnight Kitchen", "Golden Gate", "The Red Door",
            "Azure Sky", "The Black Pearl", "White Lotus", "Dragon Palace",
            "Phoenix Rising", "The Ivy Leaf", "Cedar Grove", "Willow Creek",
            "Stone Harbor", "Pine Ridge", "Oak Tree", "Maple Leaf",
            "Cherry Blossom", "Bamboo Garden", "Lotus Pond", "Rose Garden"
        ]

        # Cuisine types
        cuisine_types = [
            "Italian", "French", "Japanese", "Chinese", "Mexican",
            "Indian", "Thai", "Mediterranean", "American", "Greek",
            "Korean", "Vietnamese", "Spanish", "Turkish", "Lebanese",
            "Brazilian", "Peruvian", "Ethiopian", "Moroccan", "German"
        ]

        # Sample addresses
        addresses = [
            "123 Main Street, Downtown",
            "456 Oak Avenue, Midtown",
            "789 Pine Boulevard, Uptown",
            "321 Elm Drive, Westside",
            "654 Maple Lane, Eastside",
            "987 Cedar Road, Northside",
            "147 Birch Way, Southside",
            "258 Willow Street, Central",
            "369 Spruce Avenue, Riverside",
            "741 Ash Boulevard, Hillside",
            "852 Poplar Drive, Lakeside",
            "963 Sycamore Lane, Parkside",
            "159 Chestnut Road, Seaside",
            "357 Walnut Way, Mountainside",
            "468 Hickory Street, Countryside",
            "579 Beech Avenue, Townside",
            "680 Dogwood Boulevard, Valleyside",
            "791 Redwood Drive, Creekside",
            "802 Magnolia Lane, Meadowside",
            "913 Cypress Road, Forestside"
        ]

        # Sample descriptions
        descriptions = [
            "Experience fine dining with our carefully crafted menu featuring fresh, locally sourced ingredients.",
            "A cozy family restaurant serving traditional recipes passed down through generations.",
            "Modern cuisine meets classic flavors in our contemporary dining space with stunning city views.",
            "Authentic flavors and warm hospitality await you at our charming neighborhood restaurant.",
            "Fresh ingredients, innovative dishes, and exceptional service in a relaxed atmosphere.",
            "Discover culinary excellence with our seasonal menu and extensive wine selection.",
            "A perfect blend of tradition and innovation, offering unforgettable dining experiences.",
            "Casual dining with a focus on quality ingredients and creative presentation.",
            "Indulge in our chef's signature dishes while enjoying live music and entertainment.",
            "Farm-to-table dining featuring organic ingredients and sustainable practices.",
            "Elegant atmosphere combined with bold flavors and artistic presentation.",
            "Family-owned restaurant serving hearty portions and comfort food favorites.",
            "Contemporary design meets culinary artistry in our sophisticated dining room.",
            "Waterfront dining with fresh seafood and panoramic harbor views.",
            "Intimate setting perfect for romantic dinners and special celebrations.",
            "Bustling atmosphere with an open kitchen and interactive dining experience.",
            "Rooftop dining with craft cocktails and small plates under the stars.",
            "Historic building housing modern cuisine with a nod to culinary traditions.",
            "Vibrant flavors and colorful dishes in a lively, energetic environment.",
            "Quiet corner spot perfect for business lunches and casual meetups."
        ]

        created_restaurants = []
        
        for i in range(count):
            # Use modulo to cycle through the lists if count > list length
            name = restaurant_names[i % len(restaurant_names)]
            cuisine = random.choice(cuisine_types)
            address = addresses[i % len(addresses)]
            description = descriptions[i % len(descriptions)]
            
            # Generate unique email based on restaurant name
            email_name = name.lower().replace(' ', '').replace('&', 'and')
            email = f"{email_name}@restaurant.com"
            
            # Generate phone number
            phone = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Generate price (between $15.00 and $150.00)
            price = Decimal(f"{random.randint(15, 150)}.{random.randint(0, 99):02d}")
            
            # Ensure unique names by appending number if needed
            unique_name = name
            counter = 1
            while Restaurant.objects.filter(name=unique_name).exists():
                unique_name = f"{name} {counter}"
                counter += 1
            
            # Generate max guest count (between 10 and 100)
            max_guest_count = random.randint(10, 100)
            
            restaurant = Restaurant.objects.create(
                name=unique_name,
                address=address,
                email=email,
                phone_number=phone,
                cuisine_type=cuisine,
                price=price,
                description=description,
                max_guest_count=max_guest_count
            )
            
            # Add placeholder image if requested
            if with_images and REQUESTS_AVAILABLE:
                try:
                    # Use a food/restaurant image service
                    image_width = 800
                    image_height = 600
                    image_url = f"https://picsum.photos/{image_width}/{image_height}?random={i}"
                    
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Create filename
                        image_name = f"restaurant_{restaurant.id}_{unique_name.lower().replace(' ', '_').replace('&', 'and')}.jpg"
                        restaurant.image_url.save(
                            image_name,
                            ContentFile(response.content),
                            save=True
                        )
                        self.stdout.write(f"  ✓ Image added for {unique_name}")
                    else:
                        self.stdout.write(f"  ⚠ Failed to download image for {unique_name}")
                except Exception as e:
                    self.stdout.write(f"  ⚠ Image error for {unique_name}: {str(e)}")
            elif with_images and not REQUESTS_AVAILABLE:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠ Cannot download images: 'requests' library not installed. "
                        "Install with: pip install requests"
                    )
                )
            
            created_restaurants.append(restaurant)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_restaurants)} restaurants'
            )
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY OF CREATED RESTAURANTS:')
        self.stdout.write('='*50)
        
        for restaurant in created_restaurants[:5]:  # Show first 5 as examples
            self.stdout.write(
                f"• {restaurant.name} ({restaurant.cuisine_type}) - ${restaurant.price} - Max guests: {restaurant.max_guest_count}"
            )
        
        if len(created_restaurants) > 5:
            self.stdout.write(f"... and {len(created_restaurants) - 5} more restaurants")
        
        self.stdout.write(f"\nTotal restaurants in database: {Restaurant.objects.count()}")