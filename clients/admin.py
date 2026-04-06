from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'registration_date')
    search_fields = ('last_name', 'first_name', 'phone')