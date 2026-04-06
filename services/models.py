from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"

class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Длительность (мин)")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    categories = models.ManyToManyField(Category, through='ServiceCategory', verbose_name="Категории")

    def __str__(self):
        return f"{self.name} - {self.price} руб."

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

class ServiceCategory(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")

    def __str__(self):
        return f"{self.service.name} → {self.category.name}"

    class Meta:
        verbose_name = "Связь услуги и категории"
        verbose_name_plural = "Связи услуг и категорий"