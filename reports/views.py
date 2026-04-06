from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import HttpResponse
from salon_project.decorators import chief_required
from procedures.models import PerformedProcedure
from .forms import DateRangeForm
from .export_utils import (
    export_revenue_to_excel,
    export_staff_to_excel,
    export_services_to_excel,
    generate_line_chart, 
    generate_bar_chart, 
    generate_pie_chart, 
    export_to_pdf_revenue
)
from datetime import datetime
import base64

@chief_required
def reports_index(request):
    return render(request, 'reports/index.html')

@chief_required
def report_revenue(request):
    form = DateRangeForm(request.GET or None)
    total = 0
    daily_data = []
    start_date = None
    end_date = None
    chart = None
    has_data = False

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

    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
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

    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
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
    chart = None
    has_data = False
    procedures = PerformedProcedure.objects.all()

    if request.GET.get('export') == 'excel':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
            
            services_data = (procedures
                             .values('service__name')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            total_count = sum(item['count'] for item in services_data)
            
            for item in services_data:
                item['percent'] = round(item['count'] / total_count * 100, 1) if total_count > 0 else 0
            
            return export_services_to_excel(services_data, total_count, start_date, end_date)

    if form.is_valid() and request.GET.get('submit'):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        procedures = PerformedProcedure.objects.filter(date__range=[start_datetime, end_datetime])
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
        'chart': chart,
        'has_data': has_data,
    })