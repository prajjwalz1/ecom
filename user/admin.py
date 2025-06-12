from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Register your models here.
# accounts/admin.py


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Exclude 'last_login' to prevent it from causing an error
    exclude = ("last_login",)

    # Customize the displayed fields or fieldsets as needed
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number", "created_by")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("date_joined",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
