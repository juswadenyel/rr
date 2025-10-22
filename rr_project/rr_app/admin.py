from django.contrib import admin
from .models import User, Admin, Customer, Restaurant, Reservation, Review, Tags
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'banned'),
        }),
    )
    list_display = ['username', 'email', 'role', 'banned', 'is_staff', 'is_active']
    list_filter = ['role', 'banned', 'is_staff', 'is_active']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Reservation)
admin.site.register(Review)
admin.site.register(Tags)