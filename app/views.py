import csv
from django.http import HttpResponse
import pandas as pd
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from sklearn.linear_model import LinearRegression
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
    form_class_budjet_item = BudjetItemForm
    form_class_financial_data = FinancialDataForm

    def get_context_data(self, **kwargs):
        import numpy as np
        import json
        context = super().get_context_data(**kwargs)
        context['budjet_items'] = BudjetItem.objects.filter(plan=self.object)
        context['financial_data'] = Financial_Data.objects.filter(plan=self.object)
        context['budjet_item_form'] = kwargs.get('budjet_item_form', self.form_class_budjet_item())
        context['financial_data_form'] = kwargs.get('financial_data_form', self.form_class_financial_data())

        # Linear regression forecast
        financial_data = context['financial_data']
        if financial_data.count() > 1:
            periods = np.array([i for i, _ in enumerate(financial_data)]).reshape(-1, 1)
            values = np.array([data.actual_income_expence for data in financial_data]).reshape(-1, 1)
            model = LinearRegression().fit(periods, values)
            forecast = model.predict([[len(financial_data)]])[0][0]
            context['forecast'] = f"{forecast:,.2f}".replace(',', ' ')

            graph_labels = [data.period.strftime('%Y-%m-%d') for data in financial_data] + ["Прогноз"]
            graph_values = [float(data.actual_income_expence) for data in financial_data] + [forecast]

            # Передача графика в JSON-формате
            context['graph_data'] = json.dumps({
                "labels": graph_labels,
                "values": graph_values
            })
        else:
            context['forecast'] = "Недостаточно данных для прогноза"
            context['graph_data'] = json.dumps({
                "labels": [],
                "values": []
            })
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка добавления BudjetItem и Financial_Data."""
        self.object = self.get_object()
        budjet_item_form = self.form_class_budjet_item(request.POST or None)
        financial_data_form = self.form_class_financial_data(request.POST or None)
        # Обработка формы BudjetItem
        if 'budjet_item_submit' in request.POST:
            if budjet_item_form.is_valid():
                budjet_item = budjet_item_form.save(commit=False)
                budjet_item.plan = self.object
                budjet_item.save()
                return redirect(reverse('app:financial_plan_detail', kwargs={'pk': self.object.pk}))

        if 'financial_data_submit' in request.POST:
            if financial_data_form.is_valid():
                financial_data = financial_data_form.save(commit=False)
                financial_data.plan = self.object
                financial_data.save()
                return redirect(reverse('app:financial_plan_detail', kwargs={'pk': self.object.pk}))

        # Если формы невалидны, передаем их в контекст
        context = self.get_context_data(budjet_item_form=budjet_item_form, financial_data_form=financial_data_form)
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
