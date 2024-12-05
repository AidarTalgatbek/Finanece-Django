from django.urls import path
from . import views

app_name='app'
urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('plan/create/', views.create_financial_plan, name='create_plan')
]