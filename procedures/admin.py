from django.contrib import admin
from .models import PerformedProcedure

@admin.register(PerformedProcedure)
class PerformedProcedureAdmin(admin.ModelAdmin):
    list_display = ('client', 'employee', 'service', 'date', 'price_at_moment')
    list_filter = ('date',)