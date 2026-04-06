from django.db import models
from django.utils import timezone
from clients.models import Client
from employees.models import Employee
from services.models import Service

class PerformedProcedure(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата выполнения")
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость на момент оказания")

    def __str__(self):
        return f"{self.client} – {self.service} ({self.date.date()})"

    class Meta:
        verbose_name = "Выполненная процедура"
        verbose_name_plural = "Выполненные процедуры"