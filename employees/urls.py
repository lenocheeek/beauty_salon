from django.urls import path
from . import views

urlpatterns = [
    # Администратор
    path('', views.employee_list, name='employee_list'),
    path('add/', views.employee_add, name='employee_add'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Мастер
    path('dashboard/', views.master_dashboard, name='master_dashboard'),
    path('appointments/', views.master_appointments, name='master_appointments'),
    path('procedures/', views.master_procedures, name='master_procedures'),
]