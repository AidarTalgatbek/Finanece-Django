from django.shortcuts import render, redirect
from .forms import FinancialPlanForm, BudjetItemForm, Financial_DataForm


def main_page(request):
    return render(request, 'main_page.html')



def create_financial_plan(request):
    if request.method == "POST":
        form = FinancialPlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main_page')  # перенаправление на список планов
    else:
        form = FinancialPlanForm()
    return render(request, 'finance/create_plan.html', {'form': form})


def add_budget_item(request):
    if request.method == "POST":
        form = BudjetItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main_page')  # перенаправление на список планов
    else:
        form = BudjetItemForm()
    return render(request, 'finance/add_budget_item.html', {'form': form})


def add_financial_data(request):
    if request.method == "POST":
        form = Financial_DataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plan_list')
    else:
        form = Financial_DataForm()
    return render(request, 'finance/add_financial_data.html', {'form': form})
