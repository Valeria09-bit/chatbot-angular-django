"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path
from .views import mensaje_view, preguntar_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/mensaje/', mensaje_view),
    path('api/preguntar/', preguntar_view),
]