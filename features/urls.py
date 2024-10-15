from django.urls import path
from .views import DutchMunicipalityAPIView, ParkAPIView

urlpatterns = [
    path('features/dutch_municipality/', DutchMunicipalityAPIView.as_view(), name='municipality'),  # For creating a new feature or getting all
    path('features/dutch_municipality/<str:name>/', DutchMunicipalityAPIView.as_view(), name='municipality-specific'),  # For retrieving, updating, and deleting a feature by name
	path('features/park/', ParkAPIView.as_view(), name='park'),  # For creating a new feature or getting all
    path('features/park/<str:name>/', ParkAPIView.as_view(), name='park-specific'),  # For retrieving, updating, and deleting a feature by name
]

