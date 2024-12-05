from django import forms
from .models import FinancialPlan, BudjetItem, Financial_Data

class FinancialPlanForm(forms.ModelForm):
    class Meta:
        model = FinancialPlan
        fields = ['title', 'start_period', 'period_end', 'plan_type']

class BudjetItemForm(forms.ModelForm):
    class Meta:
        model = BudjetItem
        fields = ['plan', 'title', 'types', 'amount']

class Financial_DataForm(forms.ModelForm):
    class Meta:
        model = Financial_Data
        fields = ['plan', 'period', 'actual_income_expence', 'deviation']
