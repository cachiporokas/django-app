from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import CustomUser

from . forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    model = CustomUser
    
    list_display= ('first_name', 'last_name', 'username', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'profile_image')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username', 'email', 'password', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    
    search_fields = ('email',)
    ordering = ('email',)

# Register your models here.

admin.site.register(CustomUser, CustomUserAdmin)