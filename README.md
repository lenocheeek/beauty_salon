# GlamFlow — Система учёта процедур салона красоты

## Описание проекта

Веб-приложение для автоматизации учёта выполненных косметических процедур в салоне красоты. Система позволяет вести клиентскую базу, управлять сотрудниками и услугами, регистрировать выполненные процедуры, создавать предварительные записи, а также формировать аналитические отчёты с графиками и экспортом в Excel/PDF.

## Технологии

- Python 3.12
- Django 6.0.3
- MySQL / SQLite
- HTML, CSS, JavaScript
- Bootstrap (стили)
- matplotlib (графики)
- reportlab (PDF)
- xlsxwriter (Excel)

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/lenocheeek/beauty_salon.git
cd beauty_salon

### 2. Создать и активировать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate      # для Mac/Linux
venv\Scripts\activate         # для Windows

### 3. Установить зависимости
```bash
pip install -r requirements.txt

### 4. Настроить базу данных
По умолчанию используется SQLite (файл db.sqlite3). Для MySQL измените настройки в salon_project/settings.py.

Применить миграции:
```bash
python manage.py migrate

### 5. Создать суперпользователя
```bash
python manage.py createsuperuser
