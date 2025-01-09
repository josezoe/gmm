from rest_framework import serializers
from .models import GiftCard, GiftCardPromotion, PartyBooking, Event, Category,BaseItem, Photo, Review
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'caption']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at']

class BaseItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = BaseItem
        fields = ['id', 'name', 'description', 'slug', 'categories', 'photos', 'conditions', 'address', 'phone', 'is_active', 'reviews']
        abstract = True

class GiftCardSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        model = GiftCard
        fields = BaseItemSerializer.Meta.fields + ['base_price', 'total_value', 'stock', 'tax_included']

class GiftCardPromotionSerializer(GiftCardSerializer):
    class Meta(GiftCardSerializer.Meta):
        model = GiftCardPromotion
        fields = GiftCardSerializer.Meta.fields + ['promotional_price', 'start_date', 'end_date']

class PartyBookingSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        model = PartyBooking
        fields = BaseItemSerializer.Meta.fields + ['booking_date', 'start_time', 'end_time', 'min_guests', 'max_guests', 'guests_count']

class EventSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        model = Event
        fields = BaseItemSerializer.Meta.fields + ['event_date', 'start_time', 'end_time', 'capacity', 'tickets_available', 'price_per_ticket']