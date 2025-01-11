# vendor/models.py

from django.db import models
from django.utils import timezone
import taggit.managers
from core.models import CustomUser, State
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from core.models import Country 
from django.utils.text import slugify
from datetime import date
import uuid


class Vendor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    gst_number = models.CharField(max_length=15)
    bank_account_number = models.CharField(max_length=30)
    bank_ifsc_code = models.CharField(max_length=11)
    event_enabled = models.BooleanField(default=True)
    gift_card_enabled = models.BooleanField(default=True)
    party_booking_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.business_name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=200, blank=True)

    # Generic Foreign Key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.caption or "Photo"

class Review(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    photos = GenericRelation('Photo', related_query_name='review')

    def __str__(self):
        return f"{self.rating} stars by {self.reviewer.username} for {self.item}"

class BaseItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(Category)
    tags = taggit.managers.TaggableManager()
    photos = models.ManyToManyField(Photo)
    conditions = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class GiftCard(BaseItem):
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    tax_included = models.BooleanField(default=False)
    reviews = GenericRelation('Review')
    categories = models.ManyToManyField(Category)
    

    def clean(self):
        if self.total_value < self.base_price:
            raise ValidationError('Total value cannot be less than the base price.')

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            unique_slug = slug
            num = 1
            while GiftCard.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class GiftCardPromotion(GiftCard):
    promotional_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    

    def clean(self):
        if self.total_value < self.promotional_price:
            raise ValidationError('Total value cannot be less than the promotional price.')
        if self.end_date <= self.start_date:
            raise ValidationError('End date must be after the start date.')

    def __str__(self):
        return f"{self.name} Promotion - {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}"

class PartyBooking(BaseItem):
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    min_guests = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField()
    guests_count = models.PositiveIntegerField()
    reviews = GenericRelation('Review')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='party_bookings')
    photos = GenericRelation('Photo', related_query_name='partbooking')

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time.')
        if self.guests_count < self.min_guests or self.guests_count > self.max_guests:
            raise ValidationError(f'Number of guests must be between {self.min_guests} and {self.max_guests}.')

    def overlaps(self, other):
        same_day = self.booking_date == other.booking_date
        return (
            same_day and
            ((self.start_time < other.end_time and self.end_time > other.start_time) or
             (other.start_time < self.end_time and other.end_time > self.start_time))
        )

    @classmethod
    def is_available(cls, vendor, date, start_time, end_time, guests_count):
        bookings = cls.objects.filter(vendor=vendor, booking_date=date, is_active=True)
        for booking in bookings:
            if booking.overlaps(PartyBooking(booking_date=date, start_time=start_time, end_time=end_time)):
                return False
        return cls.min_guests <= guests_count <= cls.max_guests

class Event(BaseItem):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    end_date = models.DateField()  # Removed default=date.today
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_capacity = models.PositiveIntegerField()
    available_tickets = models.PositiveIntegerField()
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, default="1234567890")
    photos = GenericRelation('Photo', related_query_name='event')
    terms_and_conditions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate the base slug using the vendor's business name and event name
            vendor_business_name = slugify(self.vendor.business_name)  # Use the vendor's business name
            event_name = slugify(self.name)
            base_slug = f"{vendor_business_name}-{event_name}"
            self.slug = base_slug

            # Ensure the slug is unique
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"  # Append a unique identifier

        super().save(*args, **kwargs)

    def clean(self):
        """
        Validate the event data before saving.
        """
        # Check for duplicate events with the same name and start date
        duplicate_events = Event.objects.filter(
            name=self.name,
            event_date=self.event_date
        ).exclude(pk=self.pk)  # Exclude the current event when updating

        if duplicate_events.exists():
            raise ValidationError({
                'name': 'An event with this name and start date already exists.',
                'event_date': 'An event with this name and start date already exists.'
            })

        # Ensure end_date is greater than or equal to event_date
        if self.end_date < self.event_date:
            raise ValidationError({
                'end_date': 'End date must be greater than or equal to the event date.'
            })

        # Ensure end_time is greater than start_time
        if self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'End time must be greater than start time.'
            })

        # Ensure available_tickets is less than or equal to total_capacity
        if self.available_tickets > self.total_capacity:
            raise ValidationError({
                'available_tickets': 'Available tickets cannot exceed total capacity.'
            })

    class Meta:
        # Add a unique constraint for name and event_date
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'event_date'],
                name='unique_event_name_event_date'
            )
        ]
