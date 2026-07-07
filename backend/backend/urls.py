"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path
from .views import mensaje_view, sumar_view, concatenar_view, invertir_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/mensaje/', mensaje_view),
    path('api/sumar/', sumar_view),
    path('api/concatenar/', concatenar_view),
    path('api/invertir/', invertir_view),
]