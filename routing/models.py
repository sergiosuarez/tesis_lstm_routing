from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.contrib.gis.db import models

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    geom = models.PointField()

    def __str__(self):
        return self.nombre



class Usuario(AbstractUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="usuario_set",
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="usuario_set",
        blank=True,
        help_text="Specific permissions for this user."
    )