# routing/urls.py
from django.urls import path
from .views import RoutingView, map_view

urlpatterns = [
    path('route/', RoutingView.as_view(), name='route'),
    path('map/', map_view, name='map'),
]