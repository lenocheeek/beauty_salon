from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('clients/', include('clients.urls')),
    path('employees/', include('employees.urls')),
    path('services/', include('services.urls')),
    path('procedures/', include('procedures.urls')),
    path('appointments/', include('appointments.urls')),
    path('reports/', include('reports.urls')),
    path('', home_redirect, name='home'),
]