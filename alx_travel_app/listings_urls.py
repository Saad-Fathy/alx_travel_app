"""
URL configuration for listings app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'bookings', views.BookingViewSet, basename='booking')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('listings/<uuid:listing_id>/reviews/', views.ListingReviewsView.as_view(), name='listing-reviews'),
    path('listings/<uuid:listing_id>/bookings/', views.ListingBookingsView.as_view(), name='listing-bookings'),
    path('search/', views.ListingSearchView.as_view(), name='listing-search'),
]

app_name = 'listings'