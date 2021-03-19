from django.urls import path
from . import views
from .views import MyProductsListView, ProductDetailView, ProductListView, RateCreateView, RateDetailView, RateListView, ProductRatesListView
urlpatterns = [
    path('my_devices/',MyProductsListView.as_view(),name='my_devices'),
    path('products/list/',ProductListView.as_view(),name='products-list'),
    path('products/<int:pk>/',ProductDetailView.as_view(),name='products-detail'),
    path('products/rates/<int:pk>/',ProductRatesListView.as_view(),name='products-rates-list'),
    path('rates/list/',RateListView.as_view(),name='rates-list'),
    path('rate/',RateCreateView.as_view(),name='rate'),
    path('rates/<int:pk>/',RateDetailView.as_view(),name='rates-detail'),
    # product side
    path('product_ip/',views.product_ip),
    #path('store/')
    path('product/<int:current_version>/update/',views.product_update),
    
    #path('api/cash/',vie)#browser/get_full_cash
]