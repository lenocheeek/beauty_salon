from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """Только для пользователей из группы 'Администратор'"""
    def test(user):
        return user.is_authenticated and user.groups.filter(name='Администратор').exists()
    return user_passes_test(test)(view_func)

def chief_required(view_func):
    """Для руководителей и администраторов (оба могут смотреть отчёты)"""
    def test(user):
        return user.is_authenticated and (
            user.groups.filter(name='Руководитель').exists() or 
            user.groups.filter(name='Администратор').exists()
        )
    return user_passes_test(test)(view_func)