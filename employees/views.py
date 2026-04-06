from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from salon_project.decorators import admin_required
from .models import Employee
from .forms import EmployeeForm
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
    
    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'search_query': search_query,
    })

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
    
    # Клиенты, у которых были процедуры с этим мастером
    clients = Client.objects.filter(
        performedprocedure__employee=employee
    ).distinct().order_by('last_name')
    
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
    """Просмотр карточки клиента мастером"""
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    
    employee = request.user.employee
    client = get_object_or_404(Client, pk=pk)
    
    # Проверяем, что у этого мастера были процедуры с этим клиентом
    procedures = PerformedProcedure.objects.filter(client=client, employee=employee).order_by('-date')
    
    if not procedures.exists():
        return render(request, 'employees/no_access.html', {'message': 'У вас нет доступа к этому клиенту'})
    
    return render(request, 'employees/master_client_detail.html', {
        'client': client,
        'procedures': procedures,
        'employee': employee,
    })

@login_required
def master_appointments(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    
    employee = request.user.employee
    appointments = Appointment.objects.filter(employee=employee).order_by('-date', '-time')
    return render(request, 'employees/master_appointments.html', {
        'appointments': appointments,
        'employee': employee,
    })

@login_required
def master_procedures(request):
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    
    employee = request.user.employee
    procedures = PerformedProcedure.objects.filter(employee=employee).order_by('-date')
    return render(request, 'employees/master_procedures.html', {
        'procedures': procedures,
        'employee': employee,
    })