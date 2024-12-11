from django.db.models import Sum
from .models import *


def calculate_budget_sum(plan_id):
    return BudjetItem.objects.filter(plan_id=plan_id).aggregate(
        total_income=Sum('amount', filter=models.Q(types='income')),
        total_expense=Sum('amount', filter=models.Q(types='expense'))
    )
