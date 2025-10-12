from django.contrib import admin
from .models import User, Admin, Customer, PendingUser, Token, Code, Session
# Register your models here.

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(PendingUser)
admin.site.register(Token)
admin.site.register(Code)
admin.site.register(Session )