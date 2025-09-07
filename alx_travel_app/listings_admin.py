from django.contrib import admin
from .models import Listing, Review, Booking


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin interface for Listing model.
    """
    list_display = [
        'title', 'property_type', 'city', 'country', 'price_per_night',
        'max_guests', 'host', 'is_active', 'created_at'
    ]
    list_filter = [
        'property_type', 'country', 'city', 'is_active', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'location', 'city', 'country', 'host__username'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'average_rating', 'review_count']
    list_per_page = 25
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'property_type', 'host', 'is_active')
        }),
        ('Location', {
            'fields': ('location', 'city', 'country')
        }),
        ('Property Details', {
            'fields': ('price_per_night', 'max_guests', 'bedrooms', 'bathrooms', 'amenities')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('host')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Review model.
    """
    list_display = [
        'listing_title', 'reviewer', 'rating', 'is_active', 'created_at'
    ]
    list_filter = [
        'rating', 'is_active', 'created_at'
    ]
    search_fields = [
        'listing__title', 'reviewer__username', 'comment'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 25
    ordering = ['-created_at']
    
    def listing_title(self, obj):
        """Return the title of the associated listing."""
        return obj.listing.title
    listing_title.short_description = 'Listing'
    listing_title.admin_order_field = 'listing__title'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('listing', 'reviewer')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin interface for Booking model.
    """
    list_display = [
        'listing_title', 'guest', 'check_in_date', 'check_out_date',
        'num_guests', 'total_price', 'status', 'created_at'
    ]
    list_filter = [
        'status', 'check_in_date', 'check_out_date', 'created_at'
    ]
    search_fields = [
        'listing__title', 'guest__username', 'special_requests'
    ]
    readonly_fields = ['id', 'duration_days', 'created_at', 'updated_at']
    list_per_page = 25
    ordering = ['-created_at']
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('id', 'listing', 'guest', 'status')
        }),
        ('Dates & Guests', {
            'fields': ('check_in_date', 'check_out_date', 'duration_days', 'num_guests')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Additional Information', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def listing_title(self, obj):
        """Return the title of the associated listing."""
        return obj.listing.title
    listing_title.short_description = 'Listing'
    listing_title.admin_order_field = 'listing__title'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('listing', 'guest')
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        """Mark selected bookings as confirmed."""
        updated = queryset.update(status='confirmed')
        self.message_user(
            request,
            f'{updated} booking(s) were successfully marked as confirmed.'
        )
    mark_as_confirmed.short_description = 'Mark selected bookings as confirmed'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected bookings as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f'{updated} booking(s) were successfully marked as cancelled.'
        )
    mark_as_cancelled.short_description = 'Mark selected bookings as cancelled'