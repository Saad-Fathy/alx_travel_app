from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """
    Configuration for the listings application.
    
    This app manages travel listings, properties, and related functionality
    for the ALX Travel App platform.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'
    verbose_name = 'Travel Listings'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        try:
            import listings.signals  # noqa
        except ImportError:
            pass