from django.contrib import admin
from .models import Product, Rate, ProductIPAddress, ServerKey, ProductKey

class ServerKeyInline(admin.TabularInline):
    model = ServerKey
class ProductKeyInline(admin.TabularInline):
    model = ProductKey
class ProductIPAddressInline(admin.TabularInline):
    model = ProductIPAddress
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductKeyInline,
        ServerKeyInline,
        ProductIPAddressInline,
    ]
admin.site.register(Product,ProductAdmin)
admin.site.register(Rate)