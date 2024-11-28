from django.db import models


class Financial_Plan(models.Model):
    "Финансовые планы"
    PLANS = {
        'Перспективный': 1,
        'Текущий': 2,
        'Оперативный': 3
    }
    title = models.CharField('Название план', max_length=100)
    start_period = models.DateField('Начало период')
    period_end = models.DateField('Конец период')
    type_plan = models.CharField('Тип', max_length=16, choices=PLANS)


class Budjet_Items(models.Model):
    TYPE = {
        'Доход': 1,
        'Расход': 0
    }
    "Статьи бюджета"
    plan = models.ForeignKey(Financial_Plan, on_delete=models.CASCADE, verbose_name='План')
    title = models.CharField('Название', max_length=100)
    types = models.CharField('Тип', max_length=16, choices=TYPE)
    summa = models.IntegerField('Сумма')


class Financial_Data(models.Model):
    "Финансовые данные"
    plan = models.ForeignKey(Financial_Plan, verbose_name='План', on_delete=models.CASCADE)


class Forecast(models.Model):
    "Прогнозы"
    pass