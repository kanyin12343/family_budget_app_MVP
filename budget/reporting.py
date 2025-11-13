# budget/reporting.py

from decimal import Decimal
from calendar import monthrange
from datetime import date

from django.db.models import Sum

from .models import Transaction


def _month_bounds(year, month):
    """Return (start_date, end_date) for a given month."""
    last = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)


def monthly_kpis(budget_id, year=None, month=None):
    """
    Total income, total expense, and net for a budget.

    If year and month are given -> filter to that month.
    If not given -> use ALL transactions for that budget.
    Positive amount = income, negative amount = expense.
    """
    qs = Transaction.objects.filter(budget_id=budget_id)

    start = end = None
    if year is not None and month is not None:
        start, end = _month_bounds(year, month)
        qs = qs.filter(date__year=year, date__month=month)

    income = qs.filter(amount__gt=0).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    expense = qs.filter(amount__lt=0).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    net = income + expense

    return {
        "start": start,
        "end": end,
        "income": income,
        "expense": expense,
        "net": net,
    }


def monthly_by_category(budget_id, year=None, month=None):
    """
    Expense-only breakdown (absolute values) per category for charts.

    If year/month given -> that month only.
    If not -> all transactions.
    """
    qs = Transaction.objects.filter(budget_id=budget_id, amount__lt=0)

    if year is not None and month is not None:
        qs = qs.filter(date__year=year, date__month=month)

    rows = (
        qs.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("category__name")
    )

    result = []
    for r in rows:
        name = r["category__name"] or "Uncategorized"
        # amounts are negative for expenses; charts/tests want positive values
        total_abs = abs(Decimal(r["total"]))
        result.append({"category": name, "total": total_abs})
    return result


def recommendations(budget_id, top_n=3, year=None, month=None):
    """
    Return recommendation dicts for the top N expense categories.
    """
    cats = monthly_by_category(budget_id, year=year, month=month)
    cats_sorted = sorted(cats, key=lambda x: x["total"], reverse=True)

    recs = []
    for row in cats_sorted[:top_n]:
        cut5 = (row["total"] * Decimal("0.05")).quantize(Decimal("0.01"))
        recs.append(
            {
                "category": row["category"],
                "spend": row["total"],
                "suggestion": f"Reduce {row['category']} by about ${cut5} (~5%) next month to improve net.",
                "estimated_impact": -cut5,
            }
        )
    return recs


def what_if(budget_id, changes, year=None, month=None):
    """
    Simple what-if: apply signed deltas to the current net.

    changes: list of {"category": str, "delta": number}
    (We don't use category in logic; we just sum deltas.)
    """
    kpi = monthly_kpis(budget_id, year=year, month=month)
    delta_total = sum(Decimal(str(c.get("delta", 0))) for c in changes)
    projected = kpi["net"] + delta_total
    return {"base": kpi, "delta": delta_total, "projected_net": projected}
