from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from .models import Financial_Data, FinancialPlan, BudjetItem
from .forms import FinancialPlanForm, BudjetItemForm, Financial_DataForm


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

    def export_to_csv(self, plan_id):
        """Метод для экспорта финансовых данных в CSV."""
        data = Financial_Data.objects.filter(plan_id=plan_id).values()
        if not data:
            return None  # Возвращаем None, если данных нет.

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="financial_plan_{plan_id}.csv"'
        df.to_csv(path_or_buf=response, index=False)
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

    def get_context_data(self, **kwargs):
        """Добавляем экспортируемые данные в контекст."""
        context = super().get_context_data(**kwargs)
        data = Financial_Data.objects.filter(plan_id=self.object.id)
        context['financial_data'] = data
        return context

    def post(self, request, *args, **kwargs):
        """Обработка нажатия на кнопку 'Экспортировать в CSV'."""
        self.object = self.get_object()  # Загружаем объект для self.object
        if 'export_csv' in request.POST:
            csv_response = self.export_to_csv(self.object.id)
            if csv_response:
                return csv_response
            else:
                return HttpResponse("Нет данных для экспорта.", status=404)
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
