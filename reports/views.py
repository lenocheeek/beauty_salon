from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.http import HttpResponse
from salon_project.decorators import chief_required
from procedures.models import PerformedProcedure
from .forms import DateRangeForm
from .export_utils import (
    export_revenue_to_excel,
    export_staff_to_excel,
    export_services_to_excel,
    export_staff_to_pdf,
    export_services_to_pdf,
    generate_line_chart, 
    generate_bar_chart, 
    generate_pie_chart, 
    export_to_pdf_revenue
)
from datetime import datetime, timedelta
import base64
from django.utils import timezone
from employees.models import Employee
from services.models import Service

@chief_required
def reports_index(request):
    return render(request, 'reports/index.html')

@chief_required
def chief_dashboard(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Преобразуем даты в datetime для корректного сравнения
    today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
    week_start = datetime(start_of_week.year, start_of_week.month, start_of_week.day, 0, 0, 0)
    thirty_days_ago = today - timedelta(days=30)
    thirty_days_ago_start = datetime(thirty_days_ago.year, thirty_days_ago.month, thirty_days_ago.day, 0, 0, 0)
    
    # Выручка сегодня
    revenue_today = PerformedProcedure.objects.filter(date__gte=today_start).aggregate(total=Sum('price_at_moment'))['total'] or 0
    
    # Выручка за неделю
    revenue_week = PerformedProcedure.objects.filter(date__gte=week_start).aggregate(total=Sum('price_at_moment'))['total'] or 0
    
    # Выручка за последние 30 дней
    revenue_last_30 = PerformedProcedure.objects.filter(date__gte=thirty_days_ago_start).aggregate(total=Sum('price_at_moment'))['total'] or 0
    
    # Количество процедур за последние 30 дней
    procedures_count_last_30 = PerformedProcedure.objects.filter(date__gte=thirty_days_ago_start).count()
    
    # Количество сотрудников
    employees_count = Employee.objects.count()
    
    # Количество активных услуг
    services_count = Service.objects.filter(is_active=True).count()
    
    # Последние 5 выполненных процедур
    latest_procedures = PerformedProcedure.objects.select_related('client', 'employee', 'service').order_by('-date')[:5]
    
    return render(request, 'reports/chief_dashboard.html', {
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_last_30': revenue_last_30,
        'procedures_count_last_30': procedures_count_last_30,
        'employees_count': employees_count,
        'services_count': services_count,
        'latest_procedures': latest_procedures,
    })

@chief_required
def report_revenue(request):
    form = DateRangeForm(request.GET or None)
    total = 0
    daily_data = []
    start_date = None
    end_date = None
    chart = None
    has_data = False

    # Экспорт в Excel
    if request.GET.get('export') == 'excel':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("""
                SELECT DATE(date) as day, COUNT(*) as count, SUM(price_at_moment) as total
                FROM procedures_performedprocedure
                WHERE date BETWEEN %s AND %s
                GROUP BY DATE(date)
                ORDER BY day
            """, [start_datetime, end_datetime])
            
            rows = cursor.fetchall()
            for row in rows:
                if row[0]:
                    daily_data.append({
                        'day': row[0],
                        'count': row[1],
                        'total': float(row[2]) if row[2] else 0
                    })
            
            total = sum(item['total'] for item in daily_data)
            return export_revenue_to_excel(daily_data, total, start_date, end_date)

    # Экспорт в PDF
    if request.GET.get('export') == 'pdf':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("""
                SELECT DATE(date) as day, COUNT(*) as count, SUM(price_at_moment) as total
                FROM procedures_performedprocedure
                WHERE date BETWEEN %s AND %s
                GROUP BY DATE(date)
                ORDER BY day
            """, [start_datetime, end_datetime])
            
            rows = cursor.fetchall()
            for row in rows:
                if row[0]:
                    daily_data.append({
                        'day': row[0],
                        'count': row[1],
                        'total': float(row[2]) if row[2] else 0
                    })
            
            total = sum(item['total'] for item in daily_data)
            
            if daily_data:
                chart_img = generate_line_chart(daily_data)
                return export_to_pdf_revenue(daily_data, total, start_date, end_date, chart_img)
            else:
                return export_to_pdf_revenue([], 0, start_date, end_date, None)

    # Обычный показ страницы
    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("""
                SELECT DATE(date) as day, COUNT(*) as count, SUM(price_at_moment) as total
                FROM procedures_performedprocedure
                WHERE date BETWEEN %s AND %s
                GROUP BY DATE(date)
                ORDER BY day
            """, [start_datetime, end_datetime])
            
            rows = cursor.fetchall()
            for row in rows:
                if row[0]:
                    daily_data.append({
                        'day': row[0],
                        'count': row[1],
                        'total': float(row[2]) if row[2] else 0
                    })
            
            total = sum(item['total'] for item in daily_data)
            has_data = True
            
            if daily_data:
                chart_img = generate_line_chart(daily_data)
                if chart_img:
                    chart_base64 = base64.b64encode(chart_img.getvalue()).decode('utf-8')
                    chart = f"data:image/png;base64,{chart_base64}"

    return render(request, 'reports/revenue.html', {
        'form': form,
        'daily_data': daily_data,
        'total': total,
        'start_date': start_date,
        'end_date': end_date,
        'chart': chart,
        'has_data': has_data,
    })

@chief_required
def report_staff_load(request):
    form = DateRangeForm(request.GET or None)
    staff_data = []
    start_date = None
    end_date = None
    chart = None
    has_data = False
    procedures = PerformedProcedure.objects.all()

    # Экспорт в Excel
    if request.GET.get('export') == 'excel':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            
            staff_data = (procedures
                          .values('employee__last_name', 'employee__first_name', 'employee__specialization')
                          .annotate(count=Count('id'))
                          .order_by('-count'))
            
            return export_staff_to_excel(staff_data, start_date, end_date)

    # Экспорт в PDF
    if request.GET.get('export') == 'pdf':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            
            staff_data = (procedures
                          .values('employee__last_name', 'employee__first_name', 'employee__specialization')
                          .annotate(count=Count('id'))
                          .order_by('-count'))
            
            chart_img = None
            if staff_data:
                chart_data = []
                for item in staff_data:
                    chart_data.append({
                        'employee': f"{item['employee__last_name']} {item['employee__first_name']}",
                        'count': item['count']
                    })
                chart_img = generate_bar_chart(chart_data, 'employee', 'count', 
                                               'Загрузка сотрудников', 'Сотрудник', 'Количество процедур')
            
            return export_staff_to_pdf(staff_data, start_date, end_date, chart_img)

    # Обычный показ страницы
    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            has_data = True

    staff_data = (procedures
                  .values('employee__last_name', 'employee__first_name', 'employee__specialization')
                  .annotate(count=Count('id'))
                  .order_by('-count'))
    
    if has_data and staff_data:
        chart_data = []
        for item in staff_data:
            chart_data.append({
                'employee': f"{item['employee__last_name']} {item['employee__first_name']}",
                'count': item['count']
            })
        
        if chart_data:
            chart_img = generate_bar_chart(chart_data, 'employee', 'count', 
                                           'Загрузка сотрудников', 'Сотрудник', 'Количество процедур')
            if chart_img:
                chart_base64 = base64.b64encode(chart_img.getvalue()).decode('utf-8')
                chart = f"data:image/png;base64,{chart_base64}"

    return render(request, 'reports/staff_load.html', {
        'form': form,
        'staff_data': staff_data,
        'start_date': start_date,
        'end_date': end_date,
        'chart': chart,
        'has_data': has_data,
    })

@chief_required
def report_services_popularity(request):
    form = DateRangeForm(request.GET or None)
    services_data = []
    total_count = 0
    start_date = None
    end_date = None
    category = None
    chart = None
    has_data = False
    procedures = PerformedProcedure.objects.all()

    # Экспорт в Excel
    if request.GET.get('export') == 'excel':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        category_id = request.GET.get('category')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            
            if category_id:
                procedures = procedures.filter(service__categories__id=category_id)
            
            services_data = (procedures
                             .values('service__name')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            total_count = sum(item['count'] for item in services_data)
            
            for item in services_data:
                item['percent'] = round(item['count'] / total_count * 100, 1) if total_count > 0 else 0
            
            return export_services_to_excel(services_data, total_count, start_date, end_date)

    # Экспорт в PDF
    if request.GET.get('export') == 'pdf':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        category_id = request.GET.get('category')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            
            if category_id:
                procedures = procedures.filter(service__categories__id=category_id)
            
            services_data = (procedures
                             .values('service__name')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            total_count = sum(item['count'] for item in services_data)
            
            for item in services_data:
                item['percent'] = round(item['count'] / total_count * 100, 1) if total_count > 0 else 0
            
            chart_img = None
            if services_data:
                chart_img = generate_pie_chart(services_data, 'service__name', 'count', 'Популярность услуг')
            
            return export_services_to_pdf(services_data, total_count, start_date, end_date, chart_img)

    # Обычный показ страницы
    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        category = form.cleaned_data['category']
        
        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = procedures.filter(date__range=[start_datetime, end_datetime])
        
        if category:
            procedures = procedures.filter(service__categories=category)
        
        has_data = True

    services_data = (procedures
                     .values('service__name')
                     .annotate(count=Count('id'))
                     .order_by('-count'))

    total_count = sum(item['count'] for item in services_data)

    for item in services_data:
        item['percent'] = round(item['count'] / total_count * 100, 1) if total_count > 0 else 0
    
    if has_data and services_data:
        chart_img = generate_pie_chart(services_data, 'service__name', 'count', 'Популярность услуг')
        if chart_img:
            chart_base64 = base64.b64encode(chart_img.getvalue()).decode('utf-8')
            chart = f"data:image/png;base64,{chart_base64}"

    return render(request, 'reports/services_popularity.html', {
        'form': form,
        'services_data': services_data,
        'total_count': total_count,
        'start_date': start_date,
        'end_date': end_date,
        'category': category,
        'chart': chart,
        'has_data': has_data,
    })