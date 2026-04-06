from django.db import models
from clients.models import Client
from employees.models import Employee
from services.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланировано'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.client} – {self.service} ({self.date} {self.time})"

    class Meta:
        verbose_name = "Предварительная запись"
        verbose_name_plural = "Предварительные записи"