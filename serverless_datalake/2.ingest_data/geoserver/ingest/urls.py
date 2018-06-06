"""geoserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path

from .views import CsvUploadView, ShpUploadView, reset_csv_s3, reset_shp_s3

urlpatterns = [
    path('csv/reset', reset_csv_s3, name="s3_csv_reset"),
    path('shp/reset', reset_shp_s3, name="s3_shp_reset"),
    path('csv/', CsvUploadView.as_view(), name="csv_upload"),
    path('shp/', ShpUploadView.as_view(), name="shp_upload"),
]
