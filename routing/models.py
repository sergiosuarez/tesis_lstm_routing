from django.db import models

# Create your models here.
from django.contrib.gis.db import models

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    geom = models.PointField()

    def __str__(self):
        return self.nombre