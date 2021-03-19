from django.contrib import admin
from .models import Address, Village, Town, State, Country

class VillageInline(admin.TabularInline):
    model = Village
    

class TownAdmin(admin.ModelAdmin):
    inlines = [
        VillageInline,
    ]
admin.site.register(Address)
admin.site.register(Village)
admin.site.register(Town, TownAdmin)
admin.site.register(State)
admin.site.register(Country)
