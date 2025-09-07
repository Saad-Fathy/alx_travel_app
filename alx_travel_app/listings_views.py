from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Listing, Review, Booking
from .serializers import (
    ListingSerializer, ListingDetailSerializer,
    ReviewSerializer, BookingSerializer
)
from .permissions import IsOwnerOrReadOnly, IsBookingGuestOrHost


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel listings.
    
    Provides CRUD operations for listings with filtering and search capabilities.
    """
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'city', 'country', 'max_guests']
    search_fields = ['title', 'description', 'location', 'city', 'country']
    ordering_fields = ['price_per_night', 'created_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return ListingDetailSerializer
        return ListingSerializer
    
    def perform_create(self, serializer):
        """Set the host as the current user when creating a listing."""
        serializer.save(host=self.request.user)
    
    @swagger_auto_schema(
        method='get',
        responses={200: ReviewSerializer(many=True)},
        operation_description="Get all reviews for a specific listing"
    )
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific listing."""
        listing = self.get_object()
        reviews = listing.reviews.filter(is_active=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        responses={200: BookingSerializer(many=True)},
        operation_description="Get all bookings for a specific listing (host only)"
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific listing (host only)."""
        listing = self.get_object()
        if request.user != listing.host:
            return Response(
                {"detail": "You don't have permission to view these bookings."},
                status=status.HTTP_403_FORBIDDEN
            )
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    """
    queryset = Review.objects.filter(is_active=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'rating']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set the reviewer as the current user when creating a review."""
        serializer.save(reviewer=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingGuestOrHost]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'status']
    ordering_fields = ['check_in_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter bookings to show only user's own bookings or bookings for user's listings."""
        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__host=user)
        )
    
    def perform_create(self, serializer):
        """Set the guest as the current user when creating a booking."""
        serializer.save(guest=self.request.user)


class ListingReviewsView(APIView):
    """
    API view to get reviews for a specific listing.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        responses={200: ReviewSerializer(many=True)},
        operation_description="Get all reviews for a specific listing"
    )
    def get(self, request, listing_id):
        """Get all reviews for a specific listing."""
        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
            reviews = listing.reviews.filter(is_active=True)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        except Listing.DoesNotExist:
            return Response(
                {"detail": "Listing not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class ListingBookingsView(APIView):
    """
    API view to get bookings for a specific listing (host only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={200: BookingSerializer(many=True)},
        operation_description="Get all bookings for a specific listing (host only)"
    )
    def get(self, request, listing_id):
        """Get all bookings for a specific listing (host only)."""
        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
            if request.user != listing.host:
                return Response(
                    {"detail": "You don't have permission to view these bookings."},
                    status=status.HTTP_403_FORBIDDEN
                )
            bookings = listing.bookings.all()
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)
        except Listing.DoesNotExist:
            return Response(
                {"detail": "Listing not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class ListingSearchView(APIView):
    """
    Advanced search view for listings with custom filtering.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Search by location", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price per night", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price per night", type=openapi.TYPE_NUMBER),
            openapi.Parameter('property_type', openapi.IN_QUERY, description="Type of property", type=openapi.TYPE_STRING),
            openapi.Parameter('min_guests', openapi.IN_QUERY, description="Minimum number of guests", type=openapi.TYPE_INTEGER),
            openapi.Parameter('amenities', openapi.IN_QUERY, description="Comma-separated list of amenities", type=openapi.TYPE_STRING),
        ],
        responses={200: ListingSerializer(many=True)},
        operation_description="Advanced search for listings with custom filters"
    )
    def get(self, request):
        """Advanced search for listings with custom filters."""
        queryset = Listing.objects.filter(is_active=True)
        
        # Location search
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(city__icontains=location) |
                Q(country__icontains=location) |
                Q(location__icontains=location)
            )
        
        # Price range filtering
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Property type filtering
        property_type = request.query_params.get('property_type')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Guest capacity filtering
        min_guests = request.query_params.get('min_guests')
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)
        
        # Amenities filtering
        amenities = request.query_params.get('amenities')
        if amenities:
            amenity_list = [amenity.strip() for amenity in amenities.split(',')]
            for amenity in amenity_list:
                queryset = queryset.filter(amenities__icontains=amenity)
        
        serializer = ListingSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)