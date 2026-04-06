from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from salon_project.decorators import admin_required
from .models import Service
from .forms import ServiceForm

@login_required
def service_list(request):
    services = Service.objects.all().order_by('name')
    return render(request, 'services/service_list.html', {'services': services})

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