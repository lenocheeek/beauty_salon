from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('add/', views.service_add, name='service_add'),
    path('<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('<int:pk>/delete/', views.service_delete, name='service_delete'),
]