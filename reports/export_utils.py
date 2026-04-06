import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import pandas as pd
from django.http import HttpResponse
from datetime import datetime
import tempfile
import os

# Регистрация шрифта для PDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Путь к скачанному шрифту
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')

# Регистрируем шрифт с поддержкой кириллицы
RUSSIAN_FONT = 'Helvetica'
if os.path.exists(FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
        RUSSIAN_FONT = 'DejaVuSans'
        print(f"✓ Russian font loaded successfully from: {FONT_PATH}")
    except Exception as e:
        print(f"✗ Error loading font: {e}")
else:
    print(f"✗ Font not found at: {FONT_PATH}")

def export_to_excel(data, filename, sheet_name="Report"):
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return response

def export_revenue_to_excel(daily_data, total, start_date, end_date):
    import xlsxwriter
    from io import BytesIO
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    header_format = workbook.add_format({'bold': True, 'bg_color': '#FFC0CB', 'border': 1})
    money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy', 'border': 1})
    
    worksheet_data = workbook.add_worksheet('Данные')
    worksheet_data.write('A1', 'Отчёт по выручке', header_format)
    worksheet_data.write('A2', f'Период: {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}')
    worksheet_data.write('A3', f'Общая выручка: {total:,.2f} ₽')
    
    headers = ['Дата', 'Кол-во процедур', 'Выручка']
    for col, header in enumerate(headers):
        worksheet_data.write(5, col, header, header_format)
    
    for row, item in enumerate(daily_data):
        worksheet_data.write(row + 6, 0, item['day'], date_format)
        worksheet_data.write(row + 6, 1, item['count'])
        worksheet_data.write(row + 6, 2, item['total'], money_format)
    
    worksheet_chart = workbook.add_worksheet('График')
    
    dates = [item['day'] for item in daily_data]
    totals = [float(item['total']) for item in daily_data]
    
    for i, (date, total_val) in enumerate(zip(dates, totals)):
        worksheet_chart.write(i, 0, date, date_format)
        worksheet_chart.write(i, 1, total_val, money_format)
    
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name': 'Выручка',
        'categories': ['График', 0, 0, len(dates) - 1, 0],
        'values': ['График', 0, 1, len(totals) - 1, 1],
        'line': {'color': '#d946ef', 'width': 2},
        'marker': {'type': 'circle', 'size': 6, 'fill': {'color': '#f472b6'}},
    })
    chart.set_title({'name': 'Динамика выручки по дням'})
    chart.set_x_axis({'name': 'Дата'})
    chart.set_y_axis({'name': 'Выручка (руб.)'})
    
    worksheet_chart.insert_chart('D2', chart, {'x_scale': 2, 'y_scale': 1.5})
    
    workbook.close()
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    response.write(output.getvalue())
    
    return response

def export_staff_to_excel(staff_data, start_date, end_date):
    import xlsxwriter
    from io import BytesIO
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    header_format = workbook.add_format({'bold': True, 'bg_color': '#FFC0CB', 'border': 1})
    
    worksheet_data = workbook.add_worksheet('Данные')
    worksheet_data.write('A1', 'Отчёт по загрузке сотрудников', header_format)
    worksheet_data.write('A2', f'Период: {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}')
    
    headers = ['Сотрудник', 'Специализация', 'Кол-во процедур']
    for col, header in enumerate(headers):
        worksheet_data.write(4, col, header, header_format)
    
    for row, item in enumerate(staff_data):
        worksheet_data.write(row + 5, 0, f"{item['employee__last_name']} {item['employee__first_name']}")
        worksheet_data.write(row + 5, 1, item['employee__specialization'] or '—')
        worksheet_data.write(row + 5, 2, item['count'])
    
    worksheet_chart = workbook.add_worksheet('График')
    
    employees = [f"{item['employee__last_name']} {item['employee__first_name']}" for item in staff_data]
    counts = [item['count'] for item in staff_data]
    
    for i, (emp, count) in enumerate(zip(employees, counts)):
        worksheet_chart.write(i, 0, emp)
        worksheet_chart.write(i, 1, count)
    
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Количество процедур',
        'categories': ['График', 0, 0, len(employees) - 1, 0],
        'values': ['График', 0, 1, len(counts) - 1, 1],
        'fill': {'color': '#f472b6'},
        'border': {'color': '#a21caf'},
    })
    chart.set_title({'name': 'Загрузка сотрудников'})
    chart.set_x_axis({'name': 'Сотрудник'})
    chart.set_y_axis({'name': 'Количество процедур'})
    
    worksheet_chart.insert_chart('D2', chart, {'x_scale': 2, 'y_scale': 1.5})
    
    workbook.close()
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="staff_load_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    response.write(output.getvalue())
    
    return response

def export_services_to_excel(services_data, total_count, start_date, end_date):
    import xlsxwriter
    from io import BytesIO
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    header_format = workbook.add_format({'bold': True, 'bg_color': '#FFC0CB', 'border': 1})
    
    worksheet_data = workbook.add_worksheet('Данные')
    worksheet_data.write('A1', 'Отчёт по популярности услуг', header_format)
    worksheet_data.write('A2', f'Период: {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}')
    worksheet_data.write('A3', f'Всего процедур: {total_count}')
    
    headers = ['Услуга', 'Кол-во выполнений', 'Доля']
    for col, header in enumerate(headers):
        worksheet_data.write(5, col, header, header_format)
    
    for row, item in enumerate(services_data):
        worksheet_data.write(row + 6, 0, item['service__name'])
        worksheet_data.write(row + 6, 1, item['count'])
        worksheet_data.write(row + 6, 2, f"{item['percent']}%")
    
    worksheet_chart = workbook.add_worksheet('График')
    
    services = [item['service__name'] for item in services_data]
    counts = [item['count'] for item in services_data]
    
    for i, (service, count) in enumerate(zip(services, counts)):
        worksheet_chart.write(i, 0, service)
        worksheet_chart.write(i, 1, count)
    
    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': 'Популярность услуг',
        'categories': ['График', 0, 0, len(services) - 1, 0],
        'values': ['График', 0, 1, len(counts) - 1, 1],
        'data_labels': {'percentage': True, 'category': True},
    })
    chart.set_title({'name': 'Распределение услуг'})
    
    worksheet_chart.insert_chart('D2', chart, {'x_scale': 2, 'y_scale': 1.5})
    
    workbook.close()
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="services_popularity_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    response.write(output.getvalue())
    
    return response

def generate_line_chart(daily_data):
    if not daily_data:
        return None
    
    valid_data = [item for item in daily_data if item['day'] is not None]
    if not valid_data:
        return None
    
    dates = [item['day'] for item in valid_data]
    totals = [float(item['total']) for item in valid_data]
    
    plt.figure(figsize=(12, 6), facecolor='white')
    plt.plot(dates, totals, marker='o', color='#d946ef', linewidth=2.5, markersize=8, 
             markerfacecolor='#f472b6', markeredgecolor='#a21caf')
    plt.fill_between(dates, totals, 0, alpha=0.2, color='#d946ef')
    plt.title('Динамика выручки по дням', fontsize=16, fontweight='bold', color='#a21caf', pad=20)
    plt.xlabel('Дата', fontsize=12, fontweight='500')
    plt.ylabel('Выручка (руб.)', fontsize=12, fontweight='500')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def generate_bar_chart(data, x_key, y_key, title, xlabel, ylabel):
    if not data:
        return None
    
    labels = [str(item[x_key])[:30] for item in data]
    values = [item[y_key] for item in data]
    
    if not values:
        return None
    
    pink_colors = ['#f472b6', '#f78fc9', '#fba5d4', '#fec3e5', '#ffd9f0', '#e85ca3', '#d946ef', '#c026d3']
    
    plt.figure(figsize=(12, 6), facecolor='white')
    bars = plt.bar(labels, values, color=pink_colors[:len(labels)], edgecolor='#a21caf', linewidth=1.5)
    
    plt.title(title, fontsize=16, fontweight='bold', color='#a21caf', pad=20)
    plt.xlabel(xlabel, fontsize=12, fontweight='500')
    plt.ylabel(ylabel, fontsize=12, fontweight='500')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    max_val = max(values) if values else 0
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_val*0.01,
                 str(val), ha='center', va='bottom', fontsize=10, fontweight='bold', color='#a21caf')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def generate_pie_chart(data, key, value_key, title):
    if not data:
        return None
    
    labels = [str(item[key])[:30] for item in data]
    values = [item[value_key] for item in data]
    
    if not values:
        return None
    
    pink_colors = ['#f472b6', '#f78fc9', '#fba5d4', '#fec3e5', '#ffd9f0', '#e85ca3', '#d946ef', '#c026d3']
    
    plt.figure(figsize=(10, 8), facecolor='white')
    
    wedges, texts, autotexts = plt.pie(values, labels=labels, autopct='%1.1f%%',
                                        colors=pink_colors[:len(labels)], startangle=90,
                                        textprops={'fontsize': 10, 'color': '#4a1d6d'})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    plt.title(title, fontsize=16, fontweight='bold', color='#a21caf', pad=20)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

# ==================== PDF ФУНКЦИИ ====================

def export_to_pdf_revenue(daily_data, total, start_date, end_date, chart_img=None):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, textColor=colors.purple, fontName=RUSSIAN_FONT)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName=RUSSIAN_FONT)
    heading2_style = ParagraphStyle('Heading2Style', parent=styles['Heading2'], fontName=RUSSIAN_FONT, textColor=colors.purple)
    
    elements = []
    
    elements.append(Paragraph("Отчёт по выручке", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Общая выручка: {total:,.2f} руб.", heading2_style))
    elements.append(Spacer(1, 0.3*inch))
    
    temp_file = None
    if chart_img:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(chart_img.getvalue())
            temp_file = tmp.name
        
        img = Image(temp_file, width=6*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    
    valid_data = [item for item in daily_data if item['day'] is not None]
    
    table_data = [['Дата', 'Кол-во процедур', 'Выручка (руб.)']]
    for item in valid_data:
        table_data.append([
            item['day'].strftime('%d.%m.%Y'),
            str(item['count']),
            f"{item['total']:,.2f}"
        ])
    
    if len(table_data) > 1:
        col_widths = [2*inch, 1.5*inch, 1.5*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT),
            ('FONTNAME', (0, 1), (-1, -1), RUSSIAN_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Нет данных за выбранный период", normal_style))
    
    doc.build(elements)
    
    if temp_file and os.path.exists(temp_file):
        os.unlink(temp_file)
    
    return response

def export_staff_to_pdf(staff_data, start_date, end_date, chart_img=None):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="staff_load_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, textColor=colors.purple, fontName=RUSSIAN_FONT)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName=RUSSIAN_FONT)
    
    elements = []
    
    elements.append(Paragraph("Отчёт по загрузке сотрудников", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    temp_file = None
    if chart_img:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(chart_img.getvalue())
            temp_file = tmp.name
        
        img = Image(temp_file, width=6*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    
    table_data = [['Сотрудник', 'Специализация', 'Кол-во процедур']]
    total_procedures = 0
    for item in staff_data:
        count = item['count']
        total_procedures += count
        table_data.append([
            f"{item['employee__last_name']} {item['employee__first_name']}",
            item['employee__specialization'] or '—',
            str(count)
        ])
    
    if len(table_data) > 1:
        table_data.append(['ИТОГО', '', str(total_procedures)])
        
        col_widths = [2.5*inch, 2*inch, 1.5*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT),
            ('FONTNAME', (0, 1), (-1, -1), RUSSIAN_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.lavender),
            ('FONTNAME', (-1, -1), (-1, -1), RUSSIAN_FONT),
            ('FONTSIZE', (-1, -1), (-1, -1), 10),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Нет данных за выбранный период", normal_style))
    
    doc.build(elements)
    
    if temp_file and os.path.exists(temp_file):
        os.unlink(temp_file)
    
    return response

def export_services_to_pdf(services_data, total_count, start_date, end_date, chart_img=None):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="services_popularity_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, textColor=colors.purple, fontName=RUSSIAN_FONT)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName=RUSSIAN_FONT)
    heading2_style = ParagraphStyle('Heading2Style', parent=styles['Heading2'], fontName=RUSSIAN_FONT, textColor=colors.purple)
    
    elements = []
    
    elements.append(Paragraph("Отчёт по популярности услуг", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Всего процедур: {total_count}", heading2_style))
    elements.append(Spacer(1, 0.3*inch))
    
    temp_file = None
    if chart_img:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(chart_img.getvalue())
            temp_file = tmp.name
        
        img = Image(temp_file, width=6*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.3*inch))
    
    table_data = [['Услуга', 'Кол-во выполнений', 'Доля']]
    for item in services_data:
        table_data.append([
            item['service__name'],
            str(item['count']),
            f"{item['percent']}%"
        ])
    
    if len(table_data) > 1:
        table_data.append(['ИТОГО', str(total_count), '100%'])
        
        col_widths = [3*inch, 1.5*inch, 1.5*inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT),
            ('FONTNAME', (0, 1), (-1, -1), RUSSIAN_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.lavender),
            ('FONTNAME', (-1, -1), (-1, -1), RUSSIAN_FONT),
            ('FONTSIZE', (-1, -1), (-1, -1), 10),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Нет данных за выбранный период", normal_style))
    
    doc.build(elements)
    
    if temp_file and os.path.exists(temp_file):
        os.unlink(temp_file)
    
    return response