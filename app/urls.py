from django.urls import path
from . import views

app_name='app'
urlpatterns = [
    path('', views.mainPage, name='main_page'),
    path('plan/', views.FinancialPlanView.as_view(), name='plan'),
    path('plan/d/<int:pk>/', views.FinancialPlanDetailView.as_view(), name='financial_plan_detail'),
    path('plan/create/', views.CreatePlanView.as_view(), name='create_plan'),
    
]