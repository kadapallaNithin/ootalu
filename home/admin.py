from django.contrib import admin
from .models import Address, Village, Town, State, Country

class VillageInline(admin.TabularInline):
    model = Village
    

admin.site.register(Address)
admin.site.register(Village)
admin.site.register(Town)
admin.site.register(State)
admin.site.register(Country)
