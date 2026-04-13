from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_index, name='reports_index'),
    path('dashboard/', views.chief_dashboard, name='chief_dashboard'),
    path('revenue/', views.report_revenue, name='report_revenue'),
    path('staff/', views.report_staff_load, name='report_staff_load'),
    path('services/', views.report_services_popularity, name='report_services_popularity'),
]