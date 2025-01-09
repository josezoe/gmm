from django.db import models
from django.utils import timezone
import taggit.managers
from core.models import CustomUser, State
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from core.models import Country 

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

    def clean(self):
        if self.total_value < self.base_price:
            raise ValidationError('Total value cannot be less than the base price.')

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
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reviews = GenericRelation('Review')
    capacity = models.PositiveIntegerField()
    tickets_available = models.PositiveIntegerField()
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time.')
        if self.tickets_available > self.capacity:
            raise ValidationError('Tickets available cannot exceed event capacity.')

    def overlaps(self, other):
        same_day = self.event_date == other.event_date
        return (
            same_day and
            ((self.start_time < other.end_time and self.end_time > other.start_time) or
             (other.start_time < self.end_time and other.end_time > self.start_time))
        )

    @classmethod
    def is_available(cls, vendor, date, start_time, end_time):
        events = cls.objects.filter(vendor=vendor, event_date=date, is_active=True)
        for event in events:
            if event.overlaps(Event(event_date=date, start_time=start_time, end_time=end_time)):
                return False
        return True