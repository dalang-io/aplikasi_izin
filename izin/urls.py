from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_izin, name='submit_izin'),
    path('success/', views.success, name='success'),
]
