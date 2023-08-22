from django.db import models

# Create your models here.
class Place(models.Model):
    place_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    population = models.CharField(max_length=50)
    place_class = models.CharField(max_length=50)