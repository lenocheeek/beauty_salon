from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from salon_project.decorators import admin_required
from .models import Appointment
from .forms import AppointmentForm
from procedures.models import PerformedProcedure

@login_required
def appointment_list(request):
    appointments_list = Appointment.objects.select_related('client', 'employee', 'service').order_by('date', 'time')
    
    search_query = request.GET.get('q', '')
    if search_query:
        appointments_list = appointments_list.filter(
            models.Q(client__last_name__icontains=search_query) |
            models.Q(client__first_name__icontains=search_query) |
            models.Q(service__name__icontains=search_query) |
            models.Q(employee__last_name__icontains=search_query)
        )
    
    paginator = Paginator(appointments_list, 10)
    page_number = request.GET.get('page')
    appointments = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'appointments/_appointments_table.html', {'appointments': appointments})
    
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments, 'search_query': search_query})

@admin_required
def appointment_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Новая запись'})

@admin_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Редактировать запись'})

@admin_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointments/appointment_confirm_delete.html', {'appointment': appointment})

@admin_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        PerformedProcedure.objects.create(
            client=appointment.client,
            employee=appointment.employee,
            service=appointment.service,
            price_at_moment=appointment.service.price,
            date=appointment.date
        )
        appointment.status = 'completed'
        appointment.save()
        return redirect('appointment_list')
    return render(request, 'appointments/appointment_complete.html', {'appointment': appointment})