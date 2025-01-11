from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Vendor, GiftCard, GiftCardPromotion, PartyBooking, Event, Category, Photo, Review
from .forms import GiftCardForm, GiftCardPromotionForm, PartyBookingForm, EventForm, CategoryForm, PhotoForm, ReviewForm, VendorSignupForm, VendorProfileForm
from .serializers import GiftCardSerializer, GiftCardPromotionSerializer, PartyBookingSerializer, EventSerializer, CategorySerializer, PhotoSerializer, ReviewSerializer
from core.models import CustomUser, State, Country
import logging
from django.views.decorators.csrf import csrf_exempt  # remove for production
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import GiftCardForm, GiftCardPromotionForm, PartyBookingForm, EventForm, CategoryForm, PhotoForm, ReviewForm, VendorSignupForm, VendorProfileForm, VendorSettingsForm
from django.core.exceptions import ValidationError
# vendor/views.py

@login_required
def toggle_event_status(request, event_id):
    event = get_object_or_404(Event, id=event_id, vendor=request.user)
    event.is_active = not event.is_active
    event.save()
    return HttpResponseRedirect(reverse('event_list'))

def vendor_signup(request):
    if request.method == 'POST':
        form = VendorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created! Awaiting approval.")
            return redirect('vendor_login')
    else:
        form = VendorSignupForm()
    return render(request, 'vendor/signup.html', {'form': form})

def vendor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use .get() to avoid KeyError
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            print(f"User {user.username} logged in. Redirecting to dashboard.")
            return redirect('vendor_dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return render(request, 'vendor/login.html')  # Return here if authentication fails
    else:
        return render(request, 'vendor/login.html')  

def vendor_logout(request):
    logout(request)
    return redirect('vendor_login')

@login_required
def vendor_dashboard(request):
    if hasattr(request.user, 'vendor'):
        vendor = request.user.vendor
        gift_cards = GiftCard.objects.filter(vendor=vendor)
        promotions = GiftCardPromotion.objects.filter(vendor=vendor)
        bookings = PartyBooking.objects.filter(vendor=vendor)
        events = Event.objects.filter(vendor=vendor)
        context = {
            'vendor': vendor,
            'gift_cards': gift_cards,
            'promotions': promotions,
            'bookings': bookings,
            'events': events,
        }
        return render(request, 'vendor/dashboard.html', context)
    else:
        raise PermissionDenied("You do not have permission to access this page.")

@login_required
def vendor_profile(request):
    if hasattr(request.user, 'vendor'):
        vendor = request.user.vendor
        if request.method == 'POST':
            form = VendorProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('vendor_profile')
        else:
            form = VendorProfileForm(instance=request.user)
        return render(request, 'vendor/profile.html', {'form': form})
    else:
        raise PermissionDenied("You do not have permission to access this page.")

@login_required
def vendor_settings(request):
    if hasattr(request.user, 'vendor'):
        vendor = request.user.vendor
        if request.method == 'POST':
            form = VendorSettingsForm(request.POST, instance=vendor)
            if form.is_valid():
                form.save()
                messages.success(request, 'Settings updated successfully!')
                return redirect('vendor_settings')
        else:
            form = VendorSettingsForm(instance=vendor)
        return render(request, 'vendor/settings.html', {'form': form})
    else:
        raise PermissionDenied("You do not have permission to access this page.")

@login_required
def manage_items(request, item_type):
    if not hasattr(request.user, 'vendor'):
        return render(request, 'vendor/access_denied.html')

    model_map = {
        'giftcard': GiftCard,
        'giftcardpromotion': GiftCardPromotion,
        'partybooking': PartyBooking,
        'event': Event
    }
    form_map = {
        'giftcard': GiftCardForm,
        'giftcardpromotion': GiftCardPromotionForm,
        'partybooking': PartyBookingForm,
        'event': EventForm
    }
    Model = model_map.get(item_type.lower())
    Form = form_map.get(item_type.lower())

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.vendor = request.user.vendor
            item.save()
            messages.success(request, f"{item_type.capitalize()} created successfully.")
            return redirect('manage_items', item_type=item_type)
    else:
        form = Form()
    
    items = Model.objects.filter(vendor=request.user.vendor)
    context = {'form': form, 'items': items, 'item_type': item_type}
    return render(request, 'vendor/manage_items.html', context)

class VendorSettingsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, model):
        if hasattr(self.request.user, 'vendor'):
            return model.objects.filter(vendor=self.request.user.vendor)
        return model.objects.none()

    def update_active_status(self, request, model, pk):
        obj = get_object_or_404(self.get_queryset(model), pk=pk)
        obj.is_active = not obj.is_active
        obj.save()
        serializer = getattr(self, f"{model.__name__}Serializer")(obj)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        model_name = self.kwargs.get('model_name').lower()
        model_map = {
            'giftcard': GiftCard,
            'giftcardpromotion': GiftCardPromotion,
            'partybooking': PartyBooking,
            'event': Event
        }
        model = model_map.get(model_name)
        if model is None:
            return Response({'error': 'Invalid model name'}, status=400)
        
        return self.update_active_status(request, model, pk)

@csrf_exempt
@login_required
def create_gift_card(request):
    if request.method == 'POST':
        form = GiftCardForm(request.POST, request.FILES)
        if form.is_valid():
            gift_card = form.save(commit=False)
            gift_card.vendor = request.user.vendor
            gift_card.save()
            
            # Handle multiple file uploads
            for f in request.FILES.getlist('photos'):
                Photo.objects.create(image=f, gift_card=gift_card)
            
            form.save_m2m()  # Save the many-to-many data
            return redirect('some_success_url')  # Replace with your success URL
    else:
        form = GiftCardForm()
    
    return render(request, 'vendor/create_gift_card.html', {'form': form})

@csrf_exempt
@login_required
def create_gift_card_promotion(request):
    if request.method == 'POST':
        form = GiftCardPromotionForm(request.POST, request.FILES)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.vendor = request.user.vendor
            promotion.save()
            form.save_m2m()  # Save M2M fields like tags, categories, photos
            messages.success(request, "Gift card promotion created successfully.")
            return redirect('manage_gift_card_promotions')  # Redirect to where you list promotions
    else:
        form = GiftCardPromotionForm()
    return render(request, 'vendor/create_gift_card_promotion.html', {'form': form})


#events


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                event = form.save(commit=False)
                vendor = Vendor.objects.get(user=request.user)
                event.vendor = vendor
                event.save()
                return redirect('manage_items', item_type='event')
            except ValidationError as e:
                # Pass validation errors to the form
                form.add_error(None, e)
    else:
        form = EventForm()
    return render(request, 'vendor/event_form.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.all()  # Fetch all events from the database
    return render(request, 'vendor/event_list.html', {'events': events})

@login_required
def update_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            try:
                form.save()
                return redirect('manage_items', item_type='event')
            except ValidationError as e:
                # Pass validation errors to the form
                form.add_error(None, e)
    else:
        form = EventForm(instance=event)
    return render(request, 'vendor/event_form.html', {'form': form})

@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'vendor/event_confirm_delete.html', {'event': event})

@login_required
def event_detail(request, slug):  # Use slug instead of pk
    event = get_object_or_404(Event, slug=slug)  # Fetch the event by its slug
    return render(request, 'vendor/event_detail.html', {'event': event})


@login_required
def event_detail(request, slug):  # Use slug instead of pk
    event = get_object_or_404(Event, slug=slug)  # Fetch the event by its slug
    return render(request, 'vendor/event_detail.html', {'event': event})


# manage 


def manage_items(request, item_type):
    context = {}
    
    if item_type == 'giftcard':
        items = GiftCard.objects.filter(vendor=request.user.vendor)
        template = 'vendor/manage_giftcards.html'
    elif item_type == 'giftcardpromotion':
        items = GiftCardPromotion.objects.filter(vendor=request.user.vendor)
        template = 'vendor/manage_promotions.html'
    elif item_type == 'partybooking':
        items = PartyBooking.objects.filter(vendor=request.user.vendor)
        template = 'vendor/manage_bookings.html'
    elif item_type == 'event':
        items = Event.objects.filter(vendor=request.user.vendor)
        template = 'vendor/manage_events.html'
    else:
        # Handle invalid item types
        return render(request, 'vendor/error.html', {'message': 'Invalid item type'})
    
    context['items'] = items
    return render(request, template, context)