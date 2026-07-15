from django.contrib import admin
from .models import Restaurant, Customer


@admin.action(description="Approve selected restaurants")
def approve_restaurants(modeladmin, request, queryset):
    queryset.update(status="approved")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status")
    list_filter = ("status",)
    actions = [approve_restaurants]


admin.site.register(Customer)
