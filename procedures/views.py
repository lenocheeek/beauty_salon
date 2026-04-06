from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from salon_project.decorators import admin_required
from .models import PerformedProcedure
from .forms import PerformedProcedureForm

@login_required
def procedure_list(request):
    procedures_list = PerformedProcedure.objects.select_related('client', 'employee', 'service').order_by('-date')
    
    search_query = request.GET.get('q', '')
    if search_query:
        procedures_list = procedures_list.filter(
            models.Q(client__last_name__icontains=search_query) |
            models.Q(client__first_name__icontains=search_query) |
            models.Q(service__name__icontains=search_query) |
            models.Q(employee__last_name__icontains=search_query)
        )
    
    paginator = Paginator(procedures_list, 10)
    page_number = request.GET.get('page')
    procedures = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'procedures/_procedures_table.html', {'procedures': procedures})
    
    return render(request, 'procedures/procedure_list.html', {'procedures': procedures, 'search_query': search_query})

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