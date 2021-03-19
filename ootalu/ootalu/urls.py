"""ootalu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home import views as home_views
#from payments import views as payments_views
from payments.views import PostPaidCreateView

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
#from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('users.urls')),
    #path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript')),
    #path('webpush/',include('webpush.urls')),
    path('',home_views.index,name='home'),
    path(r'error/<str:message>/<str:redirect>/',home_views.error,name='error'),
    path('about/',home_views.about,name='about'),
    path('',include('product.urls')),
    path('',include('payments.urls')),
    #path('postpaid/',payments_views.postpaid,name='post-paid'),
    path('postpaid_create/<int:product_id>',PostPaidCreateView.as_view(),name='postpaid_create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

handler404 = 'home.views.file_not_found'
handler500 = 'home.views.server_error'