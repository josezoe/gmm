from django.contrib import admin
from django.utils.html import format_html
from django import forms
from taggit.models import Tag
from .models import GiftCard, GiftCardPromotion, PartyBooking, Event, Vendor, Category, Photo
from taggit.forms import TagWidget
from django.contrib.contenttypes.admin import GenericTabularInline


# Vendor Admin
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_approved', 'country')
    list_filter = ('is_approved', 'country')

    @admin.action(description='Approve selected vendors')
    def approve_vendors(self, request, queryset):
        queryset.update(is_approved=True)

    actions = [approve_vendors]

# Photo Inline 
class PhotoInline(GenericTabularInline):
    model = Photo
    extra = 1  # Number of empty photo forms to display

# GiftCard Admin
@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'base_price', 'total_value', 'is_active', 'state')
    list_filter = ('vendor', 'is_active', 'state')
    inlines = [PhotoInline]

# GiftCardPromotion Admin
@admin.register(GiftCardPromotion)
class GiftCardPromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'promotional_price', 'total_value', 'is_active', 'start_date', 'end_date', 'state')
    list_filter = ('vendor', 'is_active', 'start_date', 'end_date', 'state')
   
# PartyBooking Admin
@admin.register(PartyBooking)
class PartyBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'customer', 'booking_date', 'start_time', 'end_time', 'guests_count', 'is_active', 'state')
    list_filter = ('vendor', 'booking_date', 'is_active', 'state')
    inlines = [PhotoInline]

# Event Form (for handling tags)
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'tags': TagWidget,  # Use the TagWidget provided by taggit
        }



# Event Admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm  # Use the custom form
    list_display = ('name', 'event_date', 'vendor', 'display_image')
    readonly_fields = ('display_image', 'slug', 'phone_number', 'state')  # Make the image display read-only
    filter_horizontal = ('categories',)  # Only include categories here
    inlines = [PhotoInline]  # Add the PhotoInline for managing photos

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No Image"

    display_image.short_description = 'Image Preview'

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


