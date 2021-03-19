from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name
class State(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country,models.CASCADE,related_name='country')
    def __str__(self):
        return self.name
class Town(models.Model):
    name = models.CharField(max_length=64)
    state = models.ForeignKey(State,models.CASCADE,related_name='town')
    @property
    def details(self):
        return f"{ self.name }, { self.state }"
    def __str__(self):
        return self.name
class Village(models.Model):
    name = models.CharField(max_length=64)
    town = models.ForeignKey(Town,models.CASCADE,related_name='village')
    @property
    def details(self):
        return f"{ self.name }, { self.town.details }"
    def __str__(self):
        return self.name
class Address(models.Model):
    street = models.CharField(max_length=64)
    village = models.ForeignKey(Village,models.CASCADE,related_name='address')
    def __str__(self):
        return self.street
    @property
    def details(self):
        return f"{ self.street }, { self.village.details }"
