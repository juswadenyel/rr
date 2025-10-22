from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from rr_app.models import Restaurant
import random
import os
from django.conf import settings

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Command(BaseCommand):
    help = 'Add images to existing restaurants that do not have images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Add images to all restaurants (even those that already have images)'
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Maximum number of restaurants to add images to'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually adding images'
        )

    def handle(self, *args, **options):
        add_all = options['all']
        count = options.get('count')
        dry_run = options['dry_run']

        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('RESTAURANT IMAGE MANAGEMENT TOOL'))
        self.stdout.write('='*70)

        if not REQUESTS_AVAILABLE:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Cannot download images: 'requests' library not installed.\n"
                    "Install with: pip install requests"
                )
            )
            return

        # Get restaurants that need images
        if add_all:
            restaurants = Restaurant.objects.all()
            self.stdout.write(f"🎯 Target: ALL restaurants ({restaurants.count()} total)")
        else:
            restaurants = Restaurant.objects.filter(image__isnull=True) | Restaurant.objects.filter(image='')
            self.stdout.write(f"🎯 Target: Restaurants without images ({restaurants.count()} found)")

        if count:
            restaurants = restaurants[:count]
            self.stdout.write(f"📊 Limited to first {count} restaurants")

        if not restaurants:
            self.stdout.write(self.style.SUCCESS('✅ All restaurants already have images!'))
            return

        self.stdout.write(f"\n📷 Processing {restaurants.count()} restaurants...")

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE: No images will actually be downloaded'))
            
        processed = 0
        successful = 0
        failed = 0

        for restaurant in restaurants:
            processed += 1
            
            # Check if restaurant already has image (if not --all)
            if not add_all and restaurant.image and restaurant.image.name:
                self.stdout.write(f"  ⏭️  {restaurant.name} - Already has image")
                continue

            self.stdout.write(f"  🔄 [{processed}/{restaurants.count()}] Processing: {restaurant.name}")

            if dry_run:
                self.stdout.write(f"     🎯 Would add image to: {restaurant.name}")
                successful += 1
                continue

            try:
                # Use a restaurant/food image service with better images
                image_width = 800
                image_height = 600
                
                # Try different image services for variety
                image_services = [
                    f"https://picsum.photos/{image_width}/{image_height}?random={restaurant.id}",
                    f"https://loremflickr.com/{image_width}/{image_height}/restaurant,food?random={restaurant.id}",
                    f"https://picsum.photos/seed/{restaurant.id}/{image_width}/{image_height}"
                ]
                
                image_url = random.choice(image_services)
                
                response = requests.get(image_url, timeout=15)
                if response.status_code == 200:
                    # Create filename based on restaurant name and ID
                    clean_name = restaurant.name.lower().replace(' ', '_').replace('&', 'and').replace("'", "")
                    image_name = f"restaurant_{restaurant.id}_{clean_name}.jpg"
                    
                    # Save the image
                    restaurant.image.save(
                        image_name,
                        ContentFile(response.content),
                        save=True
                    )
                    
                    self.stdout.write(f"     ✅ Image added successfully")
                    successful += 1
                else:
                    self.stdout.write(f"     ❌ Failed to download image (Status: {response.status_code})")
                    failed += 1
                    
            except Exception as e:
                self.stdout.write(f"     ❌ Error: {str(e)}")
                failed += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('IMAGE PROCESSING SUMMARY:')
        self.stdout.write('='*50)
        self.stdout.write(f"📊 Restaurants processed: {processed}")
        self.stdout.write(f"✅ Successfully added images: {successful}")
        if failed > 0:
            self.stdout.write(f"❌ Failed: {failed}")
        
        if not dry_run:
            # Show final statistics
            total_restaurants = Restaurant.objects.count()
            restaurants_with_images = Restaurant.objects.exclude(image__isnull=True).exclude(image='').count()
            restaurants_without_images = total_restaurants - restaurants_with_images
            
            self.stdout.write(f"\n📈 FINAL STATISTICS:")
            self.stdout.write(f"   • Total restaurants: {total_restaurants}")
            self.stdout.write(f"   • Restaurants with images: {restaurants_with_images}")
            self.stdout.write(f"   • Restaurants without images: {restaurants_without_images}")
            
            if restaurants_without_images == 0:
                self.stdout.write(self.style.SUCCESS("🎉 All restaurants now have images!"))
        else:
            self.stdout.write(f"\n🔍 Run without --dry-run to actually add images")
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('IMAGE PROCESSING COMPLETE'))
        self.stdout.write('='*70)