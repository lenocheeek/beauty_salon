from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from salon_project.decorators import admin_required
from .models import PerformedProcedure
from .forms import PerformedProcedureForm
from employees.models import Employee
from services.models import Service
from datetime import datetime

@login_required
def procedure_list(request):
    procedures_list = PerformedProcedure.objects.select_related('client', 'employee', 'service').order_by('-date')
    
    # Получаем параметры фильтрации из GET-запроса
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    employee_id = request.GET.get('employee', '')
    service_id = request.GET.get('service', '')
    search_query = request.GET.get('search', '')
    
    # Фильтр по дате
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            procedures_list = procedures_list.filter(date__date__gte=start_datetime)
        except:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            procedures_list = procedures_list.filter(date__date__lte=end_datetime)
        except:
            pass
    
    # Фильтр по сотруднику
    if employee_id:
        procedures_list = procedures_list.filter(employee_id=employee_id)
    
    # Фильтр по услуге
    if service_id:
        procedures_list = procedures_list.filter(service_id=service_id)
    
    # Поиск по тексту
    if search_query:
        procedures_list = procedures_list.filter(
            models.Q(client__last_name__icontains=search_query) |
            models.Q(client__first_name__icontains=search_query) |
            models.Q(service__name__icontains=search_query) |
            models.Q(employee__last_name__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(procedures_list, 10)
    page_number = request.GET.get('page')
    procedures = paginator.get_page(page_number)
    
    # Данные для выпадающих списков
    employees = Employee.objects.all().order_by('last_name')
    services = Service.objects.filter(is_active=True).order_by('name')
    
    # Если это AJAX запрос, возвращаем только таблицу
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'procedures/_procedures_table.html', {
            'procedures': procedures,
        })
    
    return render(request, 'procedures/procedure_list.html', {
        'procedures': procedures,
        'employees': employees,
        'services': services,
        'start_date': start_date,
        'end_date': end_date,
        'employee_id': employee_id,
        'service_id': service_id,
        'search_query': search_query,
    })

@admin_required
def procedure_add(request):
    if request.method == 'POST':
        form = PerformedProcedureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('procedure_list')
    else:
        form = PerformedProcedureForm()
    return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Зарегистрировать процедуру'})

@admin_required
def procedure_edit(request, pk):
    procedure = get_object_or_404(PerformedProcedure, pk=pk)
    if request.method == 'POST':
        form = PerformedProcedureForm(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            return redirect('procedure_list')
    else:
        form = PerformedProcedureForm(instance=procedure)
    return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Редактировать процедуру'})

@admin_required
def procedure_delete(request, pk):
    procedure = get_object_or_404(PerformedProcedure, pk=pk)
    if request.method == 'POST':
        procedure.delete()
        return redirect('procedure_list')
    return render(request, 'procedures/procedure_confirm_delete.html', {'procedure': procedure})