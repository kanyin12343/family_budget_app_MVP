from django.urls import path
from . import views
from . import views_reports
from . import views_api   # NEW: API views for Expense tests

urlpatterns = [
    # Existing routes (keep exactly as-is)
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

    # ---------------------------------------------------------
    # Epic 5 — Reporting Endpoints (added safely, no conflicts)
    # ---------------------------------------------------------

    # CSV export
    path(
        'reports/<int:budget_id>/csv/',
        views_reports.reports_csv,
        name='reports_csv'
    ),

    # What-If Simulation
    path(
        'reports/<int:budget_id>/what_if/',
        views_reports.reports_what_if,
        name='reports_what_if'
    ),

    # Recommendations
    path(
        'reports/<int:budget_id>/recommendations/',
        views_reports.reports_recommendations,
        name='reports_recos'
    ),

    # ---------------------------------------------------------
    # Expense API endpoints used by tests
    # ---------------------------------------------------------

    path(
        'api/expenses/create/',
        views_api.create_expense,
        name='create_expense'
    ),
    path(
        'api/expenses/',
        views_api.list_expenses,
        name='list_expenses'
    ),
]
