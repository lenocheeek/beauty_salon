from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    specialization = models.CharField(max_length=200, blank=True, null=True, verbose_name="Специализация")
    hire_date = models.DateField(auto_now_add=True, verbose_name="Дата найма")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Пользователь")

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.specialization})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class DayOff(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='days_off', verbose_name="Сотрудник")
    date = models.DateField(verbose_name="Дата выходного")
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Причина")

    class Meta:
        unique_together = ('employee', 'date')
        verbose_name = "Выходной день"
        verbose_name_plural = "Выходные дни"

    def __str__(self):
        return f"{self.employee} - {self.date}"