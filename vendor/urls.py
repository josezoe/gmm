from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vendor-settings', views.VendorSettingsViewSet, basename='vendor-settings')

urlpatterns = [
    # Vendor Authentication
    path('signup/', views.vendor_signup, name='vendor_signup'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.vendor_logout, name='logout'),

    # Vendor Profile and Dashboard
    path('/vendordashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('profile/', views.vendor_profile, name='vendor_profile'),
    path('settings/', views.vendor_settings, name='vendor_settings'),

    # Item Management
    path('manage/<str:item_type>/', views.manage_items, name='manage_items'),
]