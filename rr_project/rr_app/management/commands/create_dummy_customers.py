from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rr_app.models import Customer

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy customers for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing customers before creating new ones'
        )

    def handle(self, *args, **options):
        clear = options['clear']

        if clear:
            Customer.objects.all().delete()
            # Also delete non-admin users
            User.objects.filter(role='CUSTOMER').delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing customers.')
            )

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
            {"username": "menumaven", "email": "menumaven@example.com", "first_name": "Amanda", "last_name": "Clark"},
            {"username": "spicygirl", "email": "spicygirl@example.com", "first_name": "Anna", "last_name": "Kim"},
            {"username": "pizzapal", "email": "pizzapal@example.com", "first_name": "Tony", "last_name": "Ricci"},
            {"username": "sushilover", "email": "sushilover@example.com", "first_name": "Yuki", "last_name": "Tanaka"},
            {"username": "burgerboy", "email": "burgerboy@example.com", "first_name": "Jake", "last_name": "Smith"},
            {"username": "veggievegan", "email": "veggievegan@example.com", "first_name": "Luna", "last_name": "Green"},
            {"username": "steakman", "email": "steakman@example.com", "first_name": "Max", "last_name": "Power"},
            {"username": "dessertdiva", "email": "dessertdiva@example.com", "first_name": "Sophie", "last_name": "Sweet"},
            {"username": "winewater", "email": "winewater@example.com", "first_name": "Oliver", "last_name": "Grape"},
            {"username": "cookiecutter", "email": "cookiecutter@example.com", "first_name": "Maya", "last_name": "Baker"},
            {"username": "noodleninja", "email": "noodleninja@example.com", "first_name": "Kai", "last_name": "Wong"}
        ]
        
        created_customers = 0
        for data in customer_data:
            if not User.objects.filter(username=data["username"]).exists():
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    password="dummypass123",
                    role='CUSTOMER'
                )
                Customer.objects.create(user=user)
                created_customers += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_customers} dummy customers')
        )
        
        self.stdout.write(f"\nTotal customers in database: {Customer.objects.count()}")
        
        # Display sample customers
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SAMPLE CUSTOMERS:')
        self.stdout.write('='*50)
        
        for customer in Customer.objects.all()[:10]:
            self.stdout.write(f"• {customer.user.first_name} {customer.user.last_name} ({customer.user.username})")