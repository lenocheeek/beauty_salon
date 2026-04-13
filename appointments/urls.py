from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('add/', views.appointment_add, name='appointment_add'),
    path('<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
    path('get_by_client/', views.get_appointments_by_client, name='get_appointments_by_client'),
    path('get_details/', views.get_appointment_details, name='get_appointment_details'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('toggle_day_off/', views.toggle_day_off, name='toggle_day_off'),
    path('add/', views.appointment_add, name='appointment_add'),
]