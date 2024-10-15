from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import DutchMunicipality, Park

class FeatureSerializer(GeoFeatureModelSerializer): # abstract feature serializer
    class Meta:
        model = None
        geo_field = "geometry"
        fields = ('id', 'name',)

class DutchMunicipalitySerializer(FeatureSerializer):
    class Meta(FeatureSerializer.Meta):
        model = DutchMunicipality

class ParkSerializer(FeatureSerializer):
    class Meta(FeatureSerializer.Meta):
        model = Park