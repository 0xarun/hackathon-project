from django.contrib import admin
from .models import Habit, WellnessEntry, HealthTip

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'unit', 'target_value', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'description')

@admin.register(WellnessEntry)
class WellnessEntryAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'value', 'created_at')
    list_filter = ('habit', 'date', 'created_at')
    search_fields = ('habit__name', 'notes')

@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ('tip', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('tip',)
