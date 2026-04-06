from django.urls import path
from . import views

urlpatterns = [
    path('', views.procedure_list, name='procedure_list'),
    path('add/', views.procedure_add, name='procedure_add'),
    path('<int:pk>/edit/', views.procedure_edit, name='procedure_edit'),
    path('<int:pk>/delete/', views.procedure_delete, name='procedure_delete'),
]