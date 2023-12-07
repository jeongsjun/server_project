from django.db import models

class CityInfo(models.Model):
    name = models.CharField(max_length=100)
    population = models.IntegerField()
    area = models.FloatField()
    # Add more fields as needed for your application

class User_Table(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    birthdate = models.DateField()

    class Meta:
        db_table='user_table'