# listings/__init__.py
# This file makes Python treat the directory as a package

# listings/apps.py
from django.apps import AppConfig

class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'

# listings/models.py
from django.db import models

# Placeholder for future models
# Example model structure for travel listings
class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

# listings/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Get all listings",
    responses={200: "Success"}
)
def get_listings(request):
    """
    Get all travel listings
    """
    return Response({"message": "Listings endpoint working"})

# listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/listings/', views.get_listings, name='get_listings'),
]

# listings/admin.py
from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at']

# listings/serializers.py
from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'