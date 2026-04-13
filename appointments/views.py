from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from calendar import monthrange, month_name
from datetime import datetime, timedelta
import json
from salon_project.decorators import admin_required
from .models import Appointment
from .forms import AppointmentForm
from procedures.models import PerformedProcedure
from employees.models import Employee, DayOff

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
    # Получаем параметры месяца для календаря
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Получаем всех сотрудников
    employees = Employee.objects.all().order_by('last_name')
    
    # Получаем выходные за месяц
    days_off = DayOff.objects.filter(date__year=year, date__month=month)
    days_off_dict = {}
    for day in days_off:
        if day.employee_id not in days_off_dict:
            days_off_dict[day.employee_id] = []
        days_off_dict[day.employee_id].append(day.date.day)
    
    month_days = range(1, monthrange(year, month)[1] + 1)
    month_name_ru = month_name[month]
    
    # Навигация по месяцам
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1])
    prev_month = first_day - timedelta(days=1)
    next_month = last_day + timedelta(days=1)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'title': 'Новая запись',
        'employees': employees,
        'month_days': month_days,
        'days_off_dict': days_off_dict,
        'year': year,
        'month': month,
        'month_name': month_name_ru,
        'prev_month': prev_month,
        'next_month': next_month,
    })

@admin_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Получаем параметры месяца для календаря
    year = int(request.GET.get('year', appointment.date.year))
    month = int(request.GET.get('month', appointment.date.month))
    
    # Получаем всех сотрудников
    employees = Employee.objects.all().order_by('last_name')
    
    # Получаем выходные за месяц
    days_off = DayOff.objects.filter(date__year=year, date__month=month)
    days_off_dict = {}
    for day in days_off:
        if day.employee_id not in days_off_dict:
            days_off_dict[day.employee_id] = []
        days_off_dict[day.employee_id].append(day.date.day)
    
    month_days = range(1, monthrange(year, month)[1] + 1)
    month_name_ru = month_name[month]
    
    # Навигация по месяцам
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1])
    prev_month = first_day - timedelta(days=1)
    next_month = last_day + timedelta(days=1)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'title': 'Редактировать запись',
        'employees': employees,
        'month_days': month_days,
        'days_off_dict': days_off_dict,
        'year': year,
        'month': month,
        'month_name': month_name_ru,
        'prev_month': prev_month,
        'next_month': next_month,
        'selected_employee_id': appointment.employee_id,
        'selected_date': appointment.date.isoformat(),
    })

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
def get_appointments_by_client(request):
    """Возвращает JSON со списком предварительных записей клиента"""
    client_id = request.GET.get('client_id')
    if client_id:
        appointments = Appointment.objects.filter(
            client_id=client_id, 
            status='scheduled'
        ).select_related('service', 'employee')
        data = [{
            'id': app.id,
            'date': app.date.strftime('%d.%m.%Y'),
            'time': app.time.strftime('%H:%M'),
            'service_name': app.service.name,
            'employee_name': f"{app.employee.last_name} {app.employee.first_name}",
            'display_text': f"{app.date.strftime('%d.%m.%Y')} {app.time.strftime('%H:%M')} - {app.service.name} ({app.employee.last_name})"
        } for app in appointments]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

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

@admin_required
def calendar_view(request):
    """Календарь занятости сотрудников для администратора"""
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1])
    
    employees = Employee.objects.all().order_by('last_name')
    
    # Все выходные за месяц
    days_off = DayOff.objects.filter(date__year=year, date__month=month)
    
    # Словарь {employee_id: [дни месяца, когда выходной]}
    days_off_dict = {}
    for day in days_off:
        if day.employee_id not in days_off_dict:
            days_off_dict[day.employee_id] = []
        days_off_dict[day.employee_id].append(day.date.day)
    
    month_days = range(1, monthrange(year, month)[1] + 1)
    month_name_ru = month_name[month]
    
    prev_month = first_day - timedelta(days=1)
    next_month = last_day + timedelta(days=1)
    
    return render(request, 'appointments/calendar.html', {
        'employees': employees,
        'month_days': month_days,
        'days_off_dict': days_off_dict,
        'year': year,
        'month': month,
        'month_name': month_name_ru,
        'prev_month': prev_month,
        'next_month': next_month,
    })

@login_required
def toggle_day_off(request):
    """API для добавления/удаления выходного дня мастера (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    if not hasattr(request.user, 'employee'):
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)
    
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    
    if not date_str:
        return JsonResponse({'error': 'Дата не указана'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Неверный формат даты'}, status=400)
    
    employee = request.user.employee
    day_off = DayOff.objects.filter(employee=employee, date=date).first()
    
    if day_off:
        day_off.delete()
        return JsonResponse({'status': 'removed', 'date': date_str})
    else:
        DayOff.objects.create(employee=employee, date=date)
        return JsonResponse({'status': 'added', 'date': date_str})