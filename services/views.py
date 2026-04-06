from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from salon_project.decorators import admin_required
from .models import Service
from .forms import ServiceForm

@login_required
def service_list(request):
    services_list = Service.objects.all().order_by('name')
    
    search_query = request.GET.get('q', '')
    if search_query:
        services_list = services_list.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    paginator = Paginator(services_list, 10)
    page_number = request.GET.get('page')
    services = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'services/_services_table.html', {'services': services})
    
    return render(request, 'services/service_list.html', {'services': services, 'search_query': search_query})

@admin_required
def service_add(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Добавить услугу'})

@admin_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Редактировать услугу'})

@admin_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})