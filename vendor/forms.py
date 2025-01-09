from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import Vendor, BaseItem, GiftCard, GiftCardPromotion, PartyBooking, Event, Category, Photo, Review, CustomUser
from core.models import CustomUser
from core.models import Country

class VendorSignupForm(UserCreationForm):
    business_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    country = forms.ModelChoiceField(queryset=Country.objects.all())

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'vendor'
        if commit:
            user.save()
        vendor = Vendor.objects.create(user=user, 
                                       business_name=self.cleaned_data['business_name'], 
                                       phone=self.cleaned_data['phone'],
                                       is_approved=False)
        return user


class VendorLoginForm(AuthenticationForm):
    pass

class VendorSettingsForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['gift_card_enabled', 'party_booking_enabled', 'event_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  #

class VendorProfileForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Include fields from CustomUser you want to edit

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add vendor specific fields here
        self.fields['business_name'] = forms.CharField(max_length=100, initial=self.instance.vendor.business_name if hasattr(self.instance, 'vendor') else '')
        self.fields['phone'] = forms.CharField(max_length=20, initial=self.instance.vendor.phone if hasattr(self.instance, 'vendor') else '')
        self.fields['address'] = forms.CharField(widget=forms.Textarea, initial=self.instance.vendor.address if hasattr(self.instance, 'vendor') else '')
        # Add other Vendor fields similarly

    def save(self, commit=True):
        user = super().save(commit=False)
        if hasattr(user, 'vendor'):
            vendor = user.vendor
            vendor.business_name = self.cleaned_data.get('business_name', vendor.business_name)
            vendor.phone = self.cleaned_data.get('phone', vendor.phone)
            vendor.address = self.cleaned_data.get('address', vendor.address)
            # Update other vendor fields here
            if commit:
                vendor.save()
        if commit:
            user.save()
        return user

class BaseItemForm(forms.ModelForm):
    class Meta:
        model = BaseItem
        fields = ['name', 'description', 'slug', 'is_active']

class GiftCardForm(BaseItemForm):
    class Meta(BaseItemForm.Meta):
        model = GiftCard
        fields = BaseItemForm.Meta.fields + ['base_price', 'total_value', 'stock', 'tax_included']

class GiftCardPromotionForm(GiftCardForm):
    class Meta(GiftCardForm.Meta):
        model = GiftCardPromotion
        fields = GiftCardForm.Meta.fields + ['promotional_price', 'start_date', 'end_date']

class PartyBookingForm(BaseItemForm):
    class Meta(BaseItemForm.Meta):
        model = PartyBooking
        fields = BaseItemForm.Meta.fields + ['booking_date', 'start_time', 'end_time', 'min_guests', 'max_guests', 'guests_count']

class EventForm(BaseItemForm):
    class Meta(BaseItemForm.Meta):
        model = Event
        fields = BaseItemForm.Meta.fields + ['event_date', 'start_time', 'end_time', 'capacity', 'tickets_available', 'price_per_ticket']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']