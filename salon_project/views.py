from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home_redirect(request):
    # Проверяем, есть ли у пользователя связанный сотрудник (мастер)
    if hasattr(request.user, 'employee') and request.user.employee:
        return redirect('master_dashboard')
    
    # Проверяем, состоит ли пользователь в группе "Руководитель"
    if request.user.groups.filter(name='Руководитель').exists():
        return redirect('reports_index')
    
    # По умолчанию — администратор (список клиентов)
    return redirect('client_list')