from django.contrib.gis.db import models

# Abstract feature
class Feature(models.Model):
    name = models.CharField(max_length=255)
    geometry = models.GeometryField()  # Geometry field can store Point, Polygon, etc

    def __str__(self):
        return self.name

    class Meta:
        abstract = True  

class DutchMunicipality(Feature):
    geometry = models.MultiPolygonField() 

    class Meta:
        db_table = "dutch_municipality"

class Park(Feature):
    geometry = models.GeometryField() # can be polygon or multipolygon

    class Meta:
        db_table = "park"
