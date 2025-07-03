from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Server, Config, Announcement, Tutorial

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = User
    # Add custom fields to the admin display if needed
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'phone_number', 'is_support_staff')
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone_number', 'is_support_staff')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('phone_number', 'is_support_staff')}),
    # )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Server)
admin.site.register(Config)
admin.site.register(Announcement)
admin.site.register(Tutorial)
