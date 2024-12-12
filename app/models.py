from django.db import models
from django.urls import reverse
from .utils import calculate_budget_sum

class FinancialPlan(models.Model):
    "Финансовые планы"
    PLANS = {
        'Перспективный': 'Перспективный',
        'Текущий': 'Текущий',
        'Оперативный': 'Оперативный'
    }
    title = models.CharField('Название план', max_length=100)
    start_period = models.DateField('Начало период')
    period_end = models.DateField('Конец период')
    plan_type = models.CharField('Тип', max_length=20, choices=PLANS)
    
    def get_absolute_url(self):
        return reverse("app:financial_plan_detail",  args=[str(self.id)])

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Финансовый план"
        verbose_name_plural = 'Финансовые планы'

class BudjetItem(models.Model):
    TYPE = {
        'income': 'Доход',
        'expense': 'Расход'
    }
    "Статьи бюджета"
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, verbose_name='План')
    title = models.CharField('Название', max_length=100)
    types = models.CharField('Тип', max_length=16, choices=TYPE)
    # summa = models.IntegerField('Сумма')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма')


class Financial_Data(models.Model):
    "Финансовые данные"
    plan = models.ForeignKey(FinancialPlan, verbose_name='План', on_delete=models.CASCADE)
    period = models.DateField('Период')
    actual_income_expence = models.DecimalField('Реальные доходы/расходы', max_digits=15, decimal_places=2)
    deviation = models.DecimalField('Отклонение от плана', max_digits=15, decimal_places=2)

    def calculate_deviation(plan_id):
        data = Financial_Data.objects.filter(plan_id=plan_id)
        for item in data:
            item.deviation = item.actual_income_expence - calculate_budget_sum(plan_id)['total_income']
            item.save()
    
    

    
class Forecast(models.Model):
    "Прогнозы"
    FORECAST_METHODS = {
        'regression': 'Регрессия',
        'time_series': 'Временные ряды',
        'other': 'Другие методы'
    }
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, verbose_name='План')
    forecast_amount = models.DecimalField('Прогнозируемая сумма', max_digits=15, decimal_places=2)
    method = models.CharField('Метод прогнозирования', max_length=20, choices=FORECAST_METHODS)
