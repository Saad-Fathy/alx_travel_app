from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Listing(models.Model):
    """
    Model representing a travel listing/property.
    """
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('cabin', 'Cabin'),
        ('hotel', 'Hotel'),
        ('resort', 'Resort'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Title of the listing")
    description = models.TextField(help_text="Detailed description of the property")
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='house')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = models.CharField(max_length=200, help_text="Property location/address")
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    amenities = models.JSONField(default=list, blank=True, help_text="List of amenities available")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}, {self.country}"
    
    @property
    def average_rating(self):
        """Calculate average rating for this listing."""
        ratings = self.reviews.filter(is_active=True).aggregate(
            avg_rating=models.Avg('rating')
        )
        return round(ratings['avg_rating'], 2) if ratings['avg_rating'] else 0.0
    
    @property
    def review_count(self):
        """Get total number of active reviews."""
        return self.reviews.filter(is_active=True).count()


class Review(models.Model):
    """
    Model representing a review for a listing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, help_text="Optional review comment")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['listing', 'reviewer']  # One review per user per listing
        indexes = [
            models.Index(fields=['listing', 'rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.listing.title} - {self.rating} stars"


class BookingStatus(models.TextChoices):
    """Choices for booking status."""
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CANCELLED = 'cancelled', 'Cancelled'
    COMPLETED = 'completed', 'Completed'


class Booking(models.Model):
    """
    Model representing a booking for a listing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    num_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    special_requests = models.TextField(blank=True, help_text="Any special requests from the guest")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'check_in_date', 'check_out_date']),
            models.Index(fields=['guest']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Booking by {self.guest.username} for {self.listing.title} ({self.check_in_date} to {self.check_out_date})"
    
    def clean(self):
        """Validate booking dates."""
        from django.core.exceptions import ValidationError
        
        if self.check_in_date >= self.check_out_date:
            raise ValidationError("Check-out date must be after check-in date.")
        
        if self.num_guests > self.listing.max_guests:
            raise ValidationError(f"Number of guests exceeds maximum capacity ({self.listing.max_guests}).")
    
    @property
    def duration_days(self):
        """Calculate the duration of the booking in days."""
        return (self.check_out_date - self.check_in_date).days