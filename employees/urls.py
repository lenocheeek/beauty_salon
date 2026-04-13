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
    path('client/<int:pk>/', views.master_client_detail, name='master_client_detail'),
    path('appointments/', views.master_appointments, name='master_appointments'),
    path('procedures/', views.master_procedures, name='master_procedures'),
    
    # Выходные дни мастера
    path('days-off/', views.my_days_off, name='my_days_off'),
    path('days-off/add/', views.add_day_off, name='add_day_off'),
    path('days-off/<int:pk>/delete/', views.delete_day_off, name='delete_day_off'),
    
    # Календарь мастера (с кликами)
    path('calendar/', views.master_calendar, name='master_calendar'),
]