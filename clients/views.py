from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from salon_project.decorators import admin_required
from .models import Client
from .forms import ClientForm

@login_required
def client_list(request):
    clients_list = Client.objects.all().order_by('last_name')
    
    search_query = request.GET.get('q', '')
    if search_query:
        clients_list = clients_list.filter(
            models.Q(last_name__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(clients_list, 10)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    
    # Если это AJAX запрос, возвращаем только таблицу
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'clients/_clients_table.html', {
            'clients': clients,
        })
    
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'search_query': search_query,
    })

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})

@admin_required
def client_add(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Добавить клиента'})

@admin_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'title': 'Редактировать клиента'})

@admin_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})