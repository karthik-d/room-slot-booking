"""roomBookingManager URL Configuration

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
from django.urls import path, include
from django.views.generic import RedirectView
from .views import MainLanding

urlpatterns = [
	path('',RedirectView.as_view(url='home',permanent=True)),
    path('admin/', admin.site.urls),
    path('cust/', include('customer_iface.urls')),
    path('manager/', include('manager_iface.urls')),
    path('users/', include('users.urls')),
    path('custom-admin/', include('admin_iface.urls')),
    path('messages/', include('messenger.urls')),
    path('api/', include('api.urls')),
    path('home', MainLanding.as_view(), name='home'),
]
