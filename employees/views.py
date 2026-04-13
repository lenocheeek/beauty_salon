from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.contrib import messages
from django.utils import timezone
from calendar import monthrange, month_name
from datetime import datetime, timedelta
from salon_project.decorators import admin_required
from .models import Employee, DayOff
from .forms import EmployeeForm, DayOffForm
from appointments.models import Appointment
from procedures.models import PerformedProcedure
from clients.models import Client

# ==================== АДМИНИСТРАТОР ====================

@login_required
def employee_list(request):
    employees_list = Employee.objects.all().order_by('last_name')
    search_query = request.GET.get('search', '')
    if search_query:
        employees_list = employees_list.filter(
            models.Q(last_name__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(specialization__icontains=search_query)
        )
    paginator = Paginator(employees_list, 10)
    page_number = request.GET.get('page')
    employees = paginator.get_page(page_number)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'employees/_employees_table.html', {'employees': employees})
    return render(request, 'employees/employee_list.html', {'employees': employees, 'search_query': search_query})

@admin_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Добавить сотрудника'})

@admin_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Редактировать сотрудника'})

@admin_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

# ==================== МАСТЕР ====================

@login_required
def master_dashboard(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Ваша учётная запись не привязана к сотруднику'})
    employee = request.user.employee
    clients = Client.objects.filter(performedprocedure__employee=employee).distinct().order_by('last_name')
    appointments = Appointment.objects.filter(employee=employee, status='scheduled').order_by('date', 'time')
    procedures = PerformedProcedure.objects.filter(employee=employee).order_by('-date')[:20]
    return render(request, 'employees/master_dashboard.html', {
        'employee': employee,
        'clients': clients,
        'appointments': appointments,
        'procedures': procedures,
    })

@login_required
def master_client_detail(request, pk):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    employee = request.user.employee
    client = get_object_or_404(Client, pk=pk)
    procedures = PerformedProcedure.objects.filter(client=client, employee=employee).order_by('-date')
    if not procedures.exists():
        return render(request, 'employees/no_access.html', {'message': 'У вас нет доступа к этому клиенту'})
    return render(request, 'employees/master_client_detail.html', {'client': client, 'procedures': procedures, 'employee': employee})

@login_required
def master_appointments(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    employee = request.user.employee
    appointments = Appointment.objects.filter(employee=employee).order_by('-date', '-time')
    return render(request, 'employees/master_appointments.html', {'appointments': appointments, 'employee': employee})

@login_required
def master_procedures(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    employee = request.user.employee
    procedures = PerformedProcedure.objects.filter(employee=employee).order_by('-date')
    return render(request, 'employees/master_procedures.html', {'procedures': procedures, 'employee': employee})

# ==================== ВЫХОДНЫЕ ДНИ МАСТЕРА ====================

@login_required
def my_days_off(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    employee = request.user.employee
    days_off = DayOff.objects.filter(employee=employee).order_by('-date')
    return render(request, 'employees/my_days_off.html', {'days_off': days_off, 'employee': employee})

@login_required
def add_day_off(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    employee = request.user.employee
    if request.method == 'POST':
        form = DayOffForm(request.POST)
        if form.is_valid():
            day_off = form.save(commit=False)
            day_off.employee = employee
            day_off.save()
            messages.success(request, f'Выходной день {day_off.date} добавлен')
            return redirect('my_days_off')
    else:
        form = DayOffForm()
    return render(request, 'employees/add_day_off.html', {'form': form, 'employee': employee})

@login_required
def delete_day_off(request, pk):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    day_off = get_object_or_404(DayOff, pk=pk, employee=request.user.employee)
    if request.method == 'POST':
        date_str = day_off.date.isoformat()
        day_off.delete()
        messages.success(request, f'Выходной день {date_str} удалён')
        return redirect('my_days_off')
    return render(request, 'employees/delete_day_off.html', {'day_off': day_off})

@login_required
def master_calendar(request):
    """Календарь выходных для мастера (с возможностью клика по ячейке)"""
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    employee = request.user.employee
    
    # Получаем дни, которые мастер уже отметил как выходные
    days_off = DayOff.objects.filter(employee=employee, date__year=year, date__month=month).values_list('date', flat=True)
    days_off_set = set(d.day for d in days_off)
    
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()  # 0 = понедельник
    days_in_month = monthrange(year, month)[1]
    
    calendar_days = []
    
    # Пустые дни перед началом месяца
    for _ in range(first_weekday):
        calendar_days.append({'empty': True})
    
    # Дни месяца
    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        calendar_days.append({
            'empty': False,
            'day': day,
            'date': date_obj.strftime('%Y-%m-%d'),
            'is_day_off': day in days_off_set
        })
    
    month_name_ru = month_name[month]
    
    # Для навигации по месяцам
    prev_month = first_day - timedelta(days=1)
    next_month = datetime(year, month, days_in_month) + timedelta(days=1)
    
    return render(request, 'employees/calendar_master.html', {
        'calendar_days': calendar_days,
        'year': year,
        'month': month,
        'month_name': month_name_ru,
        'prev_month': prev_month,
        'next_month': next_month,
    })