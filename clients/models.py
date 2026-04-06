from django.db import models

class Client(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Скидка %")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"