from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PerformedProcedure
from .forms import PerformedProcedureForm
from salon_project.decorators import admin_required, chief_required

@login_required
def procedure_list(request):
    procedures = PerformedProcedure.objects.select_related('client', 'employee', 'service').order_by('-date')
    return render(request, 'procedures/procedure_list.html', {'procedures': procedures})

@login_required
def procedure_add(request):
    if request.method == 'POST':
        form = PerformedProcedureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('procedure_list')
    else:
        form = PerformedProcedureForm()
    return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Зарегистрировать процедуру'})

@login_required
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

@login_required
def procedure_delete(request, pk):
    procedure = get_object_or_404(PerformedProcedure, pk=pk)
    if request.method == 'POST':
        procedure.delete()
        return redirect('procedure_list')
    return render(request, 'procedures/procedure_confirm_delete.html', {'procedure': procedure})