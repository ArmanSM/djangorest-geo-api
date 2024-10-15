from typing import List
import json

from django.shortcuts import get_object_or_404

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Polygon
from rest_framework_gis.filters import InBBoxFilter  

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Feature, DutchMunicipality, Park
from .serializers import DutchMunicipalitySerializer, ParkSerializer

class FeaturePagination(PageNumberPagination):

    page_size = 10  # Limit to 10 features per page
    page_size_query_param = 'page_size'
    max_page_size = 1000

class DutchMunicipalityAPIView(APIView): 

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = FeaturePagination
    bbox_filter_field = 'geometry'  # The field in the model that contains geometry (in this case, 'geometry')
    filter_backends = (InBBoxFilter,)  # Bounding box (bbox) filter

    def post(self, request):
        # Creates one or many. Note by default the input is made to conform to geojson structure so keys like 'features' are added
        
        if 'features' in request.data: 
            dutch_municipalities_to_create = bulk_feature_create_helper(request=request, feature_type=DutchMunicipality)
        
        else: 
            return Response({'error': 'Invalid GeoJSON format or empty data'}, status=status.HTTP_400_BAD_REQUEST)
        
        if dutch_municipalities_to_create:
            DutchMunicipality.objects.bulk_create(dutch_municipalities_to_create)
            return Response({'message': f'{len(dutch_municipalities_to_create)} municipalities successfully created.'}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({'error': 'No names (or only duplicate ones) detected so nothing was created'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, name=None):

        if name:
            # Retrieve a specific dutch_municipality by name
            dutch_municipality = get_object_or_404(DutchMunicipality, name=name)
            serializer = DutchMunicipalitySerializer(dutch_municipality)
            return Response(serializer.data)
        
        elif 'in_bbox' in request.query_params:
            dutch_municipalities = bbox_filter_helper(request=request, feature_type=DutchMunicipality)
       
        else:
            # Retrieve all municipalities 
            dutch_municipalities = DutchMunicipality.objects.all().order_by('name')
    
        # Paginate the results
        paginator = self.pagination_class()
        paginated_dutch_municipalities = paginator.paginate_queryset(dutch_municipalities, request)
        serializer = DutchMunicipalitySerializer(paginated_dutch_municipalities, many=True)

        return paginator.get_paginated_response(serializer.data)

    def put(self, request, name):
        # Update an existing municipality by name
        dutch_municipality = get_object_or_404(DutchMunicipality, name=name)
        serializer = DutchMunicipalitySerializer(dutch_municipality, data=request.data)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name):
        # Delete a municipality by name
        dutch_municipality = get_object_or_404(DutchMunicipality, name=name)
        dutch_municipality.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ParkAPIView(APIView): 

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = FeaturePagination
    bbox_filter_field = 'geometry'  
    filter_backends = (InBBoxFilter,)  # bounding box filter

    def post(self, request):
        # This works to create one or many as by default the input is made to conform to geojson structure 
        if 'features' in request.data: 
            parks_to_create = bulk_feature_create_helper(request=request, feature_type=Park)
        else: 
            return Response({'error': 'Invalid GeoJSON format or empty data'}, status=status.HTTP_400_BAD_REQUEST)
        Park.objects.bulk_create(parks_to_create)
        return Response({'message': f'{len(parks_to_create)} municipalities successfully created.'}, status=status.HTTP_201_CREATED)

    def get(self, request, name=None):

        if name:
            # Retrieve a specific park by name
            park = get_object_or_404(Park, name=name)
            serializer = ParkSerializer(park)
            return Response(serializer.data)
        
        elif 'in_bbox' in request.query_params:

            parks = bbox_filter_helper(request=request, feature_type=Park)

        else:

            # Retrieve all parks 
            parks = Park.objects.all().order_by('name')
    
        # Paginate the results
        paginator = self.pagination_class()
        paginated_parks = paginator.paginate_queryset(parks, request)
        serializer = ParkSerializer(paginated_parks, many=True)

        return paginator.get_paginated_response(serializer.data)

    def put(self, request, name):
        # Update an existing park by name
        park = get_object_or_404(Park, name=name)
        serializer = ParkSerializer(park, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name):
        # Delete a park by name
        park = get_object_or_404(Park, name=name)
        park.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def bbox_filter_helper(request, feature_type: Feature) -> List[Feature]: 
    """ Handles filtering by bounding box"""

    bbox = request.query_params.get('in_bbox')
            
    try:
        # Convert the string into a list of float coordinates
        bbox_list = [float(coord) for coord in bbox.split(',')]

        if len(bbox_list) != 4:
            raise ValueError('Bounding box must contain exactly 4 comma-separated coordinates.')
        
        min_x, min_y, max_x, max_y = bbox_list  # Unpack the bounding box coordinates
        bbox_polygon = Polygon.from_bbox((min_x, min_y, max_x, max_y))

        return feature_type.objects.filter(geometry__intersects=bbox_polygon).order_by('name') # return the filtered features           

    except ValueError:
        raise ValueError('Invalid bounding box coords; ensure they are all numbers')


def bulk_feature_create_helper(request, feature_type: Feature) -> List[Feature]:
    """ Handles bulk creation of features from GeoJSON FeatureCollection """

    data = request.data.get('features', [])
    features_to_create = []
    existing_names = set(feature_type.objects.values_list('name', flat=True))

    for feature_data in data:

        geometry = feature_data.get('geometry')

        if not geometry:
            raise ValueError('Feature is missing geometry')
                
        try:
            # Convert geometry to GEOSGeometry
            geometry = GEOSGeometry(json.dumps(geometry))
            feature_instance = feature_type(name=feature_data.get('properties', {}).get('name', 'Unknown'), geometry=geometry)

            # Prevents two features of the same type having the same name
            if feature_instance.name not in existing_names: 
                features_to_create.append(feature_instance)

        except Exception as e:
            raise ValueError(f"Error processing feature: {str(e)}")

    return features_to_create