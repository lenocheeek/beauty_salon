from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from salon_project.decorators import admin_required
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('client', 'employee', 'service').order_by('date', 'time')
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

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
    """Отметить запись как выполненную и создать процедуру"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        # Создаём выполненную процедуру
        from procedures.models import PerformedProcedure
        PerformedProcedure.objects.create(
            client=appointment.client,
            employee=appointment.employee,
            service=appointment.service,
            price_at_moment=appointment.service.price,
            date=appointment.date  # используем дату записи
        )
        # Обновляем статус записи
        appointment.status = 'completed'
        appointment.save()
        return redirect('appointment_list')
    return render(request, 'appointments/appointment_complete.html', {'appointment': appointment})