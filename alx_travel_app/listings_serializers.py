from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Review, Booking


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (basic info only).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    """
    reviewer = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'listing_title', 'reviewer', 'rating', 
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for Listing model (list view).
    """
    host = UserSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'property_type', 'price_per_night',
            'location', 'country', 'city', 'max_guests', 'bedrooms', 'bathrooms',
            'amenities', 'host', 'average_rating', 'review_count', 'created_at'
        ]
        read_only_fields = ['id', 'host', 'created_at', 'updated_at']
    
    def validate_price_per_night(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0.")
        return value
    
    def validate_max_guests(self, value):
        """Validate max guests is positive."""
        if value <= 0:
            raise serializers.ValidationError("Maximum guests must be greater than 0.")
        return value


class ListingDetailSerializer(ListingSerializer):
    """
    Detailed serializer for Listing model (detail view).
    """
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + ['reviews', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    guest = UserSerializer(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    listing_location = serializers.CharField(source='listing.location', read_only=True)
    host_name = serializers.CharField(source='listing.host.get_full_name', read_only=True)
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'listing_location', 'host_name',
            'guest', 'check_in_date', 'check_out_date', 'num_guests',
            'total_price', 'status', 'special_requests', 'duration_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'guest', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate booking data."""
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        num_guests = data.get('num_guests')
        listing = data.get('listing')
        
        # Validate dates
        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise serializers.ValidationError("Check-out date must be after check-in date.")
        
        # Validate guest capacity
        if listing and num_guests:
            if num_guests > listing.max_guests:
                raise serializers.ValidationError(
                    f"Number of guests ({num_guests}) exceeds maximum capacity ({listing.max_guests})."
                )
        
        return data
    
    def validate_num_guests(self, value):
        """Validate number of guests is positive."""
        if value <= 0:
            raise serializers.ValidationError("Number of guests must be greater than 0.")
        return value
    
    def validate_total_price(self, value):
        """Validate total price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than 0.")
        return value