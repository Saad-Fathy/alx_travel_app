from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        # For listings, check if user is the host
        if hasattr(obj, 'host'):
            return obj.host == request.user
        
        # For reviews, check if user is the reviewer
        if hasattr(obj, 'reviewer'):
            return obj.reviewer == request.user
        
        return False


class IsBookingGuestOrHost(permissions.BasePermission):
    """
    Custom permission to only allow booking guests or listing hosts to view/edit bookings.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Only allow guests to view/edit their own bookings,
        and hosts to view bookings for their listings.
        """
        # Guest can view/edit their own bookings
        if obj.guest == request.user:
            return True
        
        # Host can view bookings for their listings
        if obj.listing.host == request.user:
            # Hosts can only view (read-only) bookings, not modify them
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsHostOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow hosts to edit their listings.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the host of the listing
        return obj.host == request.user