# budget/views_api.py

from django.http import JsonResponse
from django.utils import timezone

from .models import Expense


def create_expense(request):
    """
    Simple API endpoint to create an Expense.

    Expected by ExpenseAPITests:
      - POST valid data -> 201, 1 record
      - POST invalid data -> 400
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Forbidden"}, status=403)

    # Extract data
    amount_raw = request.POST.get("amount")
    category = (request.POST.get("category") or "").strip()
    note = request.POST.get("note", "")

    # Basic validation
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        amount = -1  # force invalid

    if amount <= 0 or category == "":
        return JsonResponse({"detail": "Invalid expense data"}, status=400)

    exp = Expense.objects.create(
        user=request.user,
        amount=amount,
        category=category,
        note=note,
        date=timezone.now().date(),
    )

    return JsonResponse(
        {
            "id": exp.id,
            "category": exp.category,
            "amount": exp.amount,
            "note": exp.note,
        },
        status=201,
    )


def list_expenses(request):
    """
    List expenses for a given month for the logged-in user.

    Expected by ExpenseListTests:
      - GET with ?month=YYYY-MM
      - returns only that month's expenses
      - unauthenticated -> 403
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Forbidden"}, status=403)

    month_str = request.GET.get("month")
    if not month_str:
        return JsonResponse([], safe=False)

    try:
        year_str, mon_str = month_str.split("-")
        year = int(year_str)
        month = int(mon_str)
    except ValueError:
        return JsonResponse({"detail": "Invalid month format"}, status=400)

    qs = Expense.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month,
    ).order_by("date", "id")

    data = [
        {
            "category": e.category,
            "amount": e.amount,
            "note": e.note,
            "date": e.date.isoformat(),
        }
        for e in qs
    ]

    return JsonResponse(data, safe=False, status=200)
