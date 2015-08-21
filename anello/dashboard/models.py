from django.db import models

class Query(models.Model):
  payload = models.TextField()
  date = models.CharField(max_length=50)
