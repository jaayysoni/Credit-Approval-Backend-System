# credit/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # <- this is the problem
]