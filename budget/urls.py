from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Income routes
    path('income/add/', views.add_income_view, name='add_income'),
    path('income/', views.view_income, name='view_income'),
    path('income/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),

    # Expense
    path('expense/', views.add_expense_view, name='add_expense'),

    # Summary page
    path('summary/', views.summary_view, name='summary'),
]
