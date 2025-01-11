from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import create_event, event_list, update_event, delete_event,event_detail,manage_items

router = DefaultRouter()
router.register(r'vendor-settings', views.VendorSettingsViewSet, basename='vendor-settings')

urlpatterns = [
    # Vendor Authentication
    path('signup/', views.vendor_signup, name='vendor_signup'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.vendor_logout, name='logout'),

    # Vendor Profile and Dashboard
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
    path('settings/', views.vendor_settings, name='vendor_settings'),

    # Item Management
    path('manage/<str:item_type>/', views.manage_items, name='manage_items'),
    
    # gift card and promotions 
    path('gift-cards/create/', views.create_gift_card, name='create_gift_card'),
    path('gift-cards/promotions/create/', views.create_gift_card_promotion, name='create_gift_card_promotion'),

    #event
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/update/<int:pk>/', views.update_event, name='update_event'),
    path('events/delete/<int:pk>/', views.delete_event, name='delete_event'),
    path('events/<slug:slug>/', event_detail, name='event_detail'),
    #path('events/<int:pk>/', event_detail, name='event_detail'),


    #manage 
    path('manage/<str:item_type>/', views.manage_items, name='manage_items'),

]