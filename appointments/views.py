from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from salon_project.decorators import admin_required
from .models import Appointment
from .forms import AppointmentForm
from procedures.models import PerformedProcedure

@login_required
def appointment_list(request):
    appointments_list = Appointment.objects.select_related('client', 'employee', 'service').order_by('date', 'time')
    
    search_query = request.GET.get('search', '')
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
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'search_query': search_query,
    })

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

@login_required
def get_all_scheduled_appointments(request):
    """Возвращает JSON со всеми запланированными предварительными записями"""
    appointments = Appointment.objects.filter(status='scheduled').select_related('client', 'service', 'employee')
    data = [{
        'id': app.id,
        'display_text': f"{app.date.strftime('%d.%m.%Y')} {app.time.strftime('%H:%M')} - {app.client.last_name} {app.client.first_name} - {app.service.name} ({app.employee.last_name})"
    } for app in appointments]
    return JsonResponse(data, safe=False)

@login_required
def get_appointment_details(request):
    """Возвращает JSON с полной информацией о предварительной записи"""
    appointment_id = request.GET.get('appointment_id')
    if appointment_id:
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            data = {
                'id': appointment.id,
                'client_id': appointment.client.id,
                'client_name': f"{appointment.client.last_name} {appointment.client.first_name}",
                'employee_id': appointment.employee.id,
                'employee_name': f"{appointment.employee.last_name} {appointment.employee.first_name}",
                'service_id': appointment.service.id,
                'service_name': appointment.service.name,
                'service_price': float(appointment.service.price),
                'date': appointment.date.strftime('%Y-%m-%d'),
                'time': appointment.time.strftime('%H:%M'),
                'datetime_local': f"{appointment.date.strftime('%Y-%m-%d')}T{appointment.time.strftime('%H:%M')}",
                'status': appointment.status,
            }
            return JsonResponse(data)
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Запись не найдена'}, status=404)
    return JsonResponse({'error': 'ID не указан'}, status=400)