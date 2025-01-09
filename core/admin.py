from django.contrib import admin
from .models import CustomUser, Country, Currency, State, City, TimeZone, TaxSetting

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'country', 'state', 'city', 'timezone')
    list_filter = ('user_type', 'country', 'state', 'city')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'currency')

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')

@admin.register(TimeZone)
class TimeZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'timezone_value')

@admin.register(TaxSetting)
class TaxSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'country', 'state')
