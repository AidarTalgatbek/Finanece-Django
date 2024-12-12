from django import forms
from .models import FinancialPlan, BudjetItem, Financial_Data


class FinancialPlanForm(forms.ModelForm):
    start_period = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    period_end = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    class Meta:
        model = FinancialPlan
        fields = ['title', 'start_period', 'period_end', 'plan_type']

class BudjetItemForm(forms.ModelForm):
    class Meta:
        model = BudjetItem
        fields = ['title', 'types', 'amount']  # Указываем только нужные поля

class FinancialDataForm(forms.ModelForm):
    period = forms.DateField(
        label='Периода',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    class Meta:
        model = Financial_Data
        fields = ['period', 'actual_income_expence', 'deviation']