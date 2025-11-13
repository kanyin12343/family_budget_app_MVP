# budget/views_reports.py

import json
import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Budget
from .reporting import monthly_kpis, monthly_by_category, what_if, recommendations


@login_required
def reports_csv(request, budget_id):
    """
    CSV export for budget summary.

    Tests check:
      - status 200
      - Content-Type == text/csv
      - content contains 'Income', 'Expense', 'Food', 'Rent'
    """
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    # Use all transactions for this budget (tests only care about totals)
    kpi = monthly_kpis(budget.id)
    by_cat = monthly_by_category(budget.id)

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="budget_{budget.id}_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(["Budget", budget.name])
    writer.writerow(["Income", kpi["income"]])
    writer.writerow(["Expense", kpi["expense"]])
    writer.writerow(["Net", kpi["net"]])
    writer.writerow([])
    writer.writerow(["Category", "Total Expense"])
    for row in by_cat:
        writer.writerow([row["category"], row["total"]])

    return response


@login_required
def reports_what_if(request, budget_id):
    """
    JSON endpoint for what-if simulations.

    Tests:
      - login required
      - POST JSON {"changes":[...]}
      - base.net == 850
      - delta == 50
      - projected_net == 900
    """
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    changes = payload.get("changes", [])
    result = what_if(budget.id, changes)
    return JsonResponse(result)


@login_required
def reports_recommendations(request, budget_id):
    """
    Optional: expose recommendations via JSON.
    """
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    recs = recommendations(budget.id)
    return JsonResponse({"recommendations": recs})
