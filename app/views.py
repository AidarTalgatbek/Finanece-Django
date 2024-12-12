import csv
from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from .models import Financial_Data, FinancialPlan, BudjetItem
from .forms import FinancialPlanForm, BudjetItemForm, FinancialDataForm
from django.db.models import Sum



def mainPage(request):
    plans = FinancialPlan.objects.all()
    return render(request, 'main_page.html', {'plans': plans})


class FinancialPlanView(ListView):
    model = FinancialPlan
    template_name = 'finance/finance_plan.html'
    context_object_name = 'plans'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return FinancialPlan.objects.filter(
                Q(title__icontains=query) | Q(plan_type__icontains=query)
            )
        return FinancialPlan.objects.all()


class FinancialPlanDetailView(DetailView):
    model = FinancialPlan
    template_name = 'finance/plan_detail.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        """Добавляем экспортируемые данные в контекст."""
        context = super().get_context_data(**kwargs)
        data = Financial_Data.objects.filter(plan_id=self.object.id)
        context['financial_data'] = data
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка добавления BudjetItem и Financial_Data."""
        self.object = self.get_object()

        # Обработка формы BudjetItem
        budjet_form = BudjetItemForm(request.POST)
        if budjet_form.is_valid():
            budjet_item = budjet_form.save(commit=False)
            budjet_item.plan = self.object
            budjet_item.save()
            return redirect('app:plan_detail', pk=self.object.pk)

        # Обработка формы Financial_Data
        financial_data_form = FinancialDataForm(request.POST)
        if financial_data_form.is_valid():
            financial_data = financial_data_form.save(commit=False)
            financial_data.plan = self.object
            financial_data.save()
            return redirect('app:plan_detail', pk=self.object.pk)

        # Если формы невалидны, передаем их в контекст
        context = self.get_context_data()
        context['budjet_item_form'] = budjet_form
        context['financial_data_form'] = financial_data_form
        return self.render_to_response(context)

    def export_to_csv(self):
        """Экспорт данных в CSV с улучшенным форматированием."""
        plan = self.get_object()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{plan.title}_data.csv"'

        writer = csv.writer(response)

        # Заголовок
        writer.writerow([f'Financial plan: {plan.title}'])
        writer.writerow([f'Period: {plan.start_period} — {plan.period_end}'])
        writer.writerow([''])

        # Раздел для статей бюджета
        writer.writerow(['Budget items'])
        writer.writerow(['Name', 'Type', 'Sum'])
        budjet_items = BudjetItem.objects.filter(plan=plan)
        for item in budjet_items:
            writer.writerow([
                item.title,
                'Income' if item.types == 'income' else 'Consumption',
                f'{item.amount:,.2f}'.replace(',', ' ')
            ])
        writer.writerow([''])

        # Раздел для финансовых данных
        writer.writerow(['Financial data'])
        writer.writerow(['Period', 'Real income/expenses', 'Deviation from plan'])
        financial_data = Financial_Data.objects.filter(plan=plan)
        for data in financial_data:
            writer.writerow([
                data.period.strftime('%Y-%m-%d'),
                f'{data.actual_income_expence:,.2f}'.replace(',', ' '),
                f'{data.deviation:,.2f}'.replace(',', ' ')
            ])
        writer.writerow([''])

        # Итоги
        total_income = budjet_items.filter(types='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = budjet_items.filter(types='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        writer.writerow(['Results'])
        writer.writerow(['Total income', f'{total_income:,.2f}'.replace(',', ' ')])
        writer.writerow(['Total consumption', f'{total_expense:,.2f}'.replace(',', ' ')])
        writer.writerow([''])

        return response
    
    def linear_regression_forecast(self, plan_id):
        """Метод для прогноза финансовых данных с использованием линейной регрессии."""
        data = list(Financial_Data.objects.filter(plan_id=plan_id, actual_income_expence__isnull=False)
    .values_list('actual_income_expence', flat=True))
        if len(data) < 2:
            return None  # Недостаточно данных для прогноза.

        # Построение модели линейной регрессии
        x = np.arange(len(data)).reshape(-1, 1)
        y = np.array(data)
        model = LinearRegression()
        model.fit(x, y)

        # Прогноз на 12 периодов вперед
        future = model.predict([[len(data) + i] for i in range(1, 13)])
        return future.tolist()
    
    def get(self, request, *args, **kwargs):
        """Обработка GET-запроса с экспортом."""
        if 'export' in request.GET:
            return self.export_to_csv()
        return super().get(request, *args, **kwargs)


class CreatePlanView(CreateView):
    model = FinancialPlan
    form_class = FinancialPlanForm
    template_name = 'finance/create_plan.html'
    success_url = reverse_lazy('app:plan')
    
# def create_financial_plan(request):
#     if request.method == "POST":
#         form = FinancialPlanForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('main_page')  # перенаправление на список планов
#     else:
#         form = FinancialPlanForm()
#     return render(request, 'finance/create_plan.html', {'form': form})


# def add_budget_item(request):
#     if request.method == "POST":
#         form = BudjetItemForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('main_page')  # перенаправление на список планов
#     else:
#         form = BudjetItemForm()
#     return render(request, 'finance/add_budget_item.html', {'form': form})


# def add_financial_data(request):
#     if request.method == "POST":
#         form = Financial_DataForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('plan_list')
#     else:
#         form = Financial_DataForm()
#     return render(request, 'finance/add_financial_data.html', {'form': form})
