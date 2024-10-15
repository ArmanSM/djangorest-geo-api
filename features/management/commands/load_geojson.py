import requests
import geopandas as gpd
from django.core.management.base import BaseCommand
import argparse


class Command(BaseCommand):
    help = 'Load GeoJSON data into the database via the API'

    def add_arguments(self, parser):
        parser.add_argument('token', type=str, help='Authentication token (required)')
        parser.add_argument('-type', type=str, help='Feature type e.g. dutch_municipality or park', default='dutch_municipality')
        parser.add_argument('-path', type=str, help='geojson file path (likely in features/data)', default='features/data/municipalities_nl.geojson')
       
    def handle(self, *args, **kwargs):

        # Retrieve the token from command-line arguments (feature type and file path are optional)
        token = kwargs['token']
        feature_type = kwargs['type']
        file_path = kwargs['path']

        gdf = gpd.read_file(file_path)
        geojson_data = gdf.to_json()

        api_url = f'http://localhost:8000/api/features/{feature_type}/'  

        # Send POST request to the API with the provided token
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        response = requests.post(api_url, data=geojson_data, headers=headers)

        print(f'Status Code: {response.status_code}')
        print(f'Response: {response}')
