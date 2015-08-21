from django.conf.urls import include, url
from django.contrib import admin

from dashboard import views

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
]
