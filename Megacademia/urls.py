"""Megacademia URL Configuration

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
from django.urls import path
from MegacademiaAPP import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/extend/interest', views.handle_interest),
    path('api/v1/extend/upload_file', views.upload_file),
    path('api/v1/extend/sharing_file/<str:sharing_code>', views.download_file),
    path('api/v1/extend/get_csrf', views.get_csrf),
    path('api/v1/extend/search_interest', views.get_interest_statuses),
    path('api/v1/extend/get_social_network_graph/<str:user_id>', views.social_network_graph),
]
