from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Employee
from .forms import EmployeeForm
from appointments.models import Appointment
from procedures.models import PerformedProcedure

# ==================== АДМИНИСТРАТОР ====================

@login_required
def employee_list(request):
    """Список сотрудников"""
    employees = Employee.objects.all().order_by('last_name')
    return render(request, 'employees/employee_list.html', {'employees': employees})

@login_required
def employee_add(request):
    """Добавление сотрудника"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Добавить сотрудника'})

@login_required
def employee_edit(request, pk):
    """Редактирование сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Редактировать сотрудника'})

@login_required
def employee_delete(request, pk):
    """Удаление сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

# ==================== МАСТЕР ====================

@login_required
def master_dashboard(request):
    """Дашборд мастера"""
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Ваша учётная запись не привязана к сотруднику'})
    
    employee = request.user.employee
    appointments = Appointment.objects.filter(employee=employee, status='scheduled').order_by('date', 'time')
    procedures = PerformedProcedure.objects.filter(employee=employee).order_by('-date')[:20]
    
    return render(request, 'employees/master_dashboard.html', {
        'employee': employee,
        'appointments': appointments,
        'procedures': procedures,
    })

@login_required
def master_appointments(request):
    """Все записи мастера"""
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
    """Все выполненные процедуры мастера"""
    if not hasattr(request.user, 'employee'):
        return render(request, 'employees/no_access.html', {'message': 'Доступ запрещён'})
    
    employee = request.user.employee
    procedures = PerformedProcedure.objects.filter(employee=employee).order_by('-date')
    return render(request, 'employees/master_procedures.html', {
        'procedures': procedures,
        'employee': employee,
    })