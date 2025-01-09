
from django.contrib import admin
from .models import GiftCard, GiftCardPromotion, PartyBooking, Event,Vendor
from core.models import State

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_approved', 'country')
    list_filter = ('is_approved', 'country')

    @admin.action(description='Approve selected vendors')
    def approve_vendors(self, request, queryset):
        queryset.update(is_approved=True)
    actions = [approve_vendors]




@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'base_price', 'total_value', 'is_active', 'state')
    list_filter = ('vendor', 'is_active', 'state')

    @admin.action(description='Activate/Deactivate based on state')
    def toggle_active_by_state(self, request, queryset):
        state_id = request.POST.get('state_id')
        if state_id:
            state = State.objects.get(id=state_id)
            for obj in queryset:
                obj.is_active = obj.state == state
                obj.save()
        else:
            self.message_user(request, "Please select a state.")
    toggle_active_by_state.short_description = "Activate/Deactivate based on state"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'toggle_active_by_state' in actions:
            actions['toggle_active_by_state']['extra_context'] = {
                'states': State.objects.all(),
            }
        return actions

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if 'action' in request.POST and request.POST['action'] == 'toggle_active_by_state':
            extra_context['states'] = State.objects.all()
        return super().changelist_view(request, extra_context=extra_context)

# Similar changes for GiftCardPromotion, PartyBooking, and Event:

@admin.register(GiftCardPromotion)
class GiftCardPromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'promotional_price', 'total_value', 'is_active', 'start_date', 'end_date', 'state')
    list_filter = ('vendor', 'is_active', 'start_date', 'end_date', 'state')

    def vendor(self, obj):
        return obj.gift_card.vendor
    vendor.short_description = 'Vendor'  # This sets the column header in admin
    
@admin.register(PartyBooking)
class PartyBookingAdmin(GiftCardAdmin):
    list_display = ('name', 'vendor', 'customer', 'booking_date', 'start_time', 'end_time', 'guests_count', 'is_active', 'state')
    list_filter = ('vendor', 'booking_date', 'is_active', 'state')

@admin.register(Event)
class EventAdmin(GiftCardAdmin):
    list_display = ('name', 'vendor', 'event_date', 'start_time', 'end_time', 'capacity', 'tickets_available', 'is_active', 'state')
    list_filter = ('vendor', 'event_date', 'is_active', 'state')