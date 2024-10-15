# features/management/commands/add_feature.py

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from features.models import Feature
import json

class Command(BaseCommand):
    help = 'Add a specific feature to the database'

    def handle(self, *args, **kwargs):
        # Example GeoJSON data
        geojson = {
            "type": "Feature",
            "properties": {
                "name": "Appingedam"
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [30, 20],
                            [45, 40],
                            [10, 40],
                            [30, 20]
                        ]
                    ],
                    [
                        [
                            [15, 5],
                            [40, 10],
                            [10, 20],
                            [5, 10],
                            [15, 5]
                        ]
                    ]
                ]
            }
        }

        # Create and save the feature
        feature = Feature(
            name=geojson['properties']['name'],
            geom=GEOSGeometry(json.dumps(geojson['geometry']), srid=4326)  # Set the SRID to 4326 for WGS84
        )
        feature.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully added feature: {feature.name}'))
