from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.db.models import Count
from .models import Product, Rate, ProductIPAddress, ServerKey
#from payments.models import Plan
from payments import views as payments_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotModified, HttpResponseNotFound, Http404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from django.db import IntegrityError
#from django import forms
from json import JSONEncoder
import json
from django.contrib import messages
import secrets
import string
from os import path

class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        return Product.objects.all()#filter(address__village__mandal=self.request.user.address.village.mandal)

class ProductDetailView(DetailView):
    model = Product

class ProductRatesListView(ListView):
    model = Rate
    template_name = 'home/products_rates_list.html'
    context_object_name = 'rates'

    def get_queryset(self):
        product = get_object_or_404(Product,pk=self.kwargs.get('pk'))
        return Rate.objects.filter(product_id=product.id)
class MyProductsListView(LoginRequiredMixin, ListView):
#    model = Product
    template_name = 'product/my_devices.html'

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)#.annotate(id__count=Count('id'),plan__count=Count('plan')) #Plan.objects.annotate(product__count=Count('product'))#.filter(product)#Product.objects.filter(owner=self.request.user)
    def get_context_data(self):
        context = super().get_context_data()
        context['inactive__count'] = Product.objects.filter(owner=self.request.user).filter(plan__is_active=False).annotate(inactive__count=Count('plan__is_active'))
        return context
    # def get_context_data(self):
    #     context = super().get_context_data()
    #     context['count'] = Plan.
    
class RateCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Rate
    fields = ['amount','liters_per_unit','units']
    def form_valid(self,form):
        form.instance.product = Product.objects.get(id=self.request.POST['product'])
        return super().form_valid(form)
    def test_func(self):
        user = self.request.user
        if user.is_authenticated:
            return True
        return False
    def get_context_data(self):
        products = Product.objects.filter(owner=self.request.user)
        context = super().get_context_data()
        context['products'] = products
        return context
class RateListView(ListView):
    model = Rate
    context_object_name = 'rates'

class RateDetailView(DetailView):
    model = Rate

# def wrapper(request):
#     response = dict()
#     if request.method == "GET":
#         g = request.GET
#         if 'prod' in g and 'ip' in g and 'key' in g:

#         else:
#             response['code'] = 100
#             response['error'] = "Some data is missing"
#     else:
#         response['code'] = 101
#         response['error'] = "Not a get request"
#     e = JSONEncoder()
#     return HttpResponse(e.encode(response))

# def prod_ip_dev(request):
#     wrapper(request)

# def product_ip_not_using(request):
#     response = dict()
#     if request.method == "GET":
#         g = request.GET
#         if 'prod' in g and 'ip' in g and 'key' in g :
#             try:
#                 prod_ips = ProductIPAddress.objects.filter(product_id=g['prod']).order_by('-time')
#                 if len(prod_ips) >= 1:
#                     if len(prod_ips) > 100:#delete history
#                         pass
#                     prod_ip = prod_ips.first()
#                     if prod_ip.server_key == g['key']:
#                         serv_key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
#                         #serv_key = "nithinPk"
#                         new_prod_ip = ProductIPAddress.objects.create(product_id=g['prod'],ip=g['ip'],server_key=serv_key)
#                         new_prod_ip.save()
#                         response = {"key":serv_key,"password":"12345678","ssid":"kadapalla"}
#                         #response['code'] = 200 #ok
#                     elif 'reset' in g and g['reset'] == 1:# incorrectly stored api_key due to interrupted reset or powerloss
#                         if len(prod_ip.server_key) == len(g['key']):
#                             i = 0
#                             while i < len(prod_ip.server_key):
#                                 if prod_ip.server_key[i] != g['key'][i]:
#                                     break
#                                 i += 1
#                             prod_ip = prod_ips[1]
#                             while i < len(prod_ip.server_key):
#                                 if prod_ip.server_key[i] != g['key'][i]:
#                                     break
#                                 i += 1
#                             if i == len(prod_ip.server_key) - 1:
#                                 serv_key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
#                                 new_prod_ip = ProductIPAddress.objects.create(product_id=g['prod'],ip=g['ip'],server_key=serv_key)
#                                 new_prod_ip.save()
#                                 response = {"server_key":serv_key,"password":"12345678","ssid":"kadapalla"}
#                             else:
#                                 response['code'] = 403
#                                 response['error'] = "Not authenticated"
#                     else:
#                         response['code'] = 403
#                         response['error'] = "Not authenticated"
#                 else:
#                     response['code'] = 201
#                     response["error"] = 'not initialized properly'# i.e you don't have a server_key that is sent by server or product may not be present
#             except IntegrityError:
#                 response['code'] = 202
#                 response['error'] = "IntegriryError"
#             except ValueError:
#                 response['code'] = 203
#                 response['error'] = "ValueError" #may be product_id is not provided
#             except OverflowError:
#                 response['code'] = 204
#                 response['error'] = "OverflowError"
#         else:
#             response['code'] = 100
#             response['error'] = "Some data is missing"
#     else:
#         response['code'] = 101
#         response["error"] = "Not a get request"
#     e = JSONEncoder()
#     return HttpResponse(e.encode(response))#'{"api_key":"'+api_key+'","ssid":"kadapalla","password":"12345678"}'


def product_ip_func(g,**kwargs):
    if 'ip' in g and 'key' in kwargs:
        key = kwargs['key']
        new_key = ''.join(secrets.choice(string.ascii_uppercase+string.digits + string.ascii_lowercase) for _ in range(128))
        product = get_object_or_404(Product,pk=g['id'])
        product.productkey.key = new_key
        product.productkey.save()
        new_prod_ip = ProductIPAddress.objects.create(product_id=g['id'],ip=g['ip'])
        response = {"product_key":new_key }#, "update_available":1,"password":"12345678","ssid":"kadapalla"}
        if 'next' in g:
            response.update(payments_views.next_txn(product))
        return response
    return {"error":"IP is is not provided"}
def product_ip(request):
    return secure_request(request,product_ip_func)
    
def product_update(request,current_version):
    data = "404"
    try:
        path_to_file = path.join(settings.FIRMWARE_UPDATE_PATH,str(current_version))
        data = open(path_to_file,'rb').read()
        return HttpResponse(data)
    except FileNotFoundError:
        raise Http404
        #return HttpResponseNotFound()
    return HttpResponseNotModified()

# def product_update(request,current_version):
#     return secure_request(request,product_update_func)


def secure_request(request,func):
    response = dict()
    if request.method == "GET": # change to post
        g = request.GET
        if 'id' in g and 'key' in g :
            try:
#                server_keys = ServerKey.objects.filter(product_id=g['id']).order_by('-id')
#                key = server_keys[0]
                key = ServerKey.objects.filter(product_id=g['id']).first()#get_object_or_404(ServerKey,pk=g['id'])
                
                if key.key == g['key']:
                    response = func(g,key=key)

            # uncomment following if server_key reset concept is used
                # elif 'is_reset' in g and g['is_reset'] == '1':# incorrectly stored api_key due to interrupted reset or powerloss
                #     i = 0
                #     print("in reset ",len(key.key),len(g['key']))
                #     if len(key.key) == len(g['key']):
                #         while i < len(key.key):
                #             if key.key[i] != g['key'][i]:
                #                 break
                #             i += 1
                #         key = server_keys[1]
                #         while i < len(key.key):
                #             if key.key[i] != g['key'][i]:
                #                 break
                #             i += 1
                #     print("in reset i = ",i)
                #     if i == len(key.key):
                #         response = func(g,key=key)
                #     else:
                #         response['code'] = 403
                #         response['error'] = "Not authenticated"+str(i)+" "+str(len(g['key']))+key.key
                else:
                    print(g['key'],key.key)
                    response['code'] = 403
                    response['error'] = "Not Authenticated"
                # els:
                # #     response['code'] = 201
                # #     response["error"] = 'not initialized properly'# i.e you don't have a server_key that is sent by server or product may not be present
            except IntegrityError:
                response['code'] = 202
                response['error'] = "IntegriryError"
            except ValueError:
                response['code'] = 203
                response['error'] = "ValueError" #may be product_id is not provided i.e null
            except OverflowError:
                response['code'] = 204
                response['error'] = "OverflowError"
        else:
            response['code'] = 100
            response['error'] = "Some data is missing"
    else:
        response['code'] = 101
        response["error"] = "Not a get request"
    e = JSONEncoder()
    return HttpResponse(e.encode(response))#'{"api_key":"'+api_key+'","ssid":"kadapalla","password":"12345678"}'