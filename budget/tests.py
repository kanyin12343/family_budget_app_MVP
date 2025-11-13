"""
Tests for the budget app.

Sections:
1) Expense model & basic API tests
2) Epic 5 – Budget summaries & reports (stories 23–28)
"""

from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Expense, Budget, Category, Transaction


# ============================================================
# 1) Expense model & basic API tests
# ============================================================


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass123",
        )

    def test_create_expense_model_fields(self):
        """Expense model should correctly save basic fields."""
        exp = Expense.objects.create(
            user=self.user,
            amount=100.50,
            category="Food",
            note="Groceries",
            date=date.today(),
            recurring=False,
        )
        self.assertEqual(exp.amount, 100.50)
        self.assertEqual(exp.category, "Food")
        self.assertFalse(exp.recurring)


class ExpenseAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="apitester",
            password="pass123",
        )
        self.client.login(username="apitester", password="pass123")
        self.create_url = reverse("create_expense")

    def test_post_valid_expense_creates_record(self):
        """Posting valid data should create an expense and return 201."""
        data = {"amount": 25, "category": "Transport", "note": "Bus fare"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.first().category, "Transport")

    def test_post_invalid_expense_fails(self):
        """Invalid data should not create an expense and should return 400."""
        data = {"amount": -10, "category": ""}  # negative + missing category
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 400)


class ExpenseListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="listuser",
            password="pass123",
        )
        self.client.login(username="listuser", password="pass123")
        self.list_url = reverse("list_expenses")

    def test_get_monthly_expenses_returns_correct_records(self):
        """Should return expenses only for the selected month."""
        Expense.objects.create(
            user=self.user,
            amount=50,
            category="Food",
            date=date(2025, 10, 1),
        )
        Expense.objects.create(
            user=self.user,
            amount=100,
            category="Transport",
            date=date(2025, 9, 30),
        )

        response = self.client.get(self.list_url, {"month": "2025-10"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], "Food")

    def test_get_expenses_requires_login(self):
        """Unauthenticated users should get 403."""
        self.client.logout()
        response = self.client.get(self.list_url, {"month": "2025-10"})
        self.assertEqual(response.status_code, 403)


# ============================================================
# 2) Epic 5 – Budget summaries & reports (stories 23–28)
# ============================================================


class Epic5Base(TestCase):
    """
    Base fixture for Epic 5 tests.

    Creates:
      - a user
      - a budget
      - three categories (Food, Rent, Misc)
      - one income transaction + two expense transactions, all in Feb 2026
    """

    def setUp(self):
        # user + budget
        self.user = User.objects.create_user(
            username="derrick",
            password="pass123",
        )
        self.budget = Budget.objects.create(user=self.user, name="Spring Budget")

        # categories
        self.food = Category.objects.create(budget=self.budget, name="Food")
        self.rent = Category.objects.create(budget=self.budget, name="Rent")
        self.misc = Category.objects.create(budget=self.budget, name="Misc")

        # same month for all transactions: 2026-02
        d1 = date(2026, 2, 5)
        d2 = date(2026, 2, 10)
        d3 = date(2026, 2, 15)

        # income + expenses (positive = income, negative = expense)
        Transaction.objects.create(
            budget=self.budget,
            category=self.misc,
            date=d1,
            description="Paycheck",
            amount=Decimal("2000.00"),
        )
        Transaction.objects.create(
            budget=self.budget,
            category=self.rent,
            date=d2,
            description="Rent",
            amount=Decimal("-900.00"),
        )
        Transaction.objects.create(
            budget=self.budget,
            category=self.food,
            date=d3,
            description="Groceries",
            amount=Decimal("-250.00"),
        )


class MonthlySummaryTests(Epic5Base):
    """
    Covers user stories:
      23 – breakdown of monthly expenditure by category
      24 – see total income over total expenses
    """

    def test_monthly_kpis_for_budget(self):
        from budget.reporting import monthly_kpis

        kpi = monthly_kpis(self.budget.id, year=2026, month=2)

        self.assertEqual(kpi["income"], Decimal("2000.00"))
        # expenses stored negative internally
        self.assertEqual(kpi["expense"], Decimal("-1150.00"))
        self.assertEqual(kpi["net"], Decimal("850.00"))

    def test_monthly_expense_breakdown_by_category(self):
        from budget.reporting import monthly_by_category

        rows = monthly_by_category(self.budget.id, year=2026, month=2)

        # expect Food 250, Rent 900 (absolute values for charts)
        summary = {r["category"]: r["total"] for r in rows}
        self.assertEqual(summary["Food"], Decimal("250.00"))
        self.assertEqual(summary["Rent"], Decimal("900.00"))


class ExportCsvTests(Epic5Base):
    """
    Covers user story 26 – export data in CSV format.
    """

    def test_export_csv_downloads_file(self):
        self.client.login(username="derrick", password="pass123")
        url = reverse("reports_csv", args=[self.budget.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")

        content = resp.content.decode()
        # contains key lines
        self.assertIn("Income", content)
        self.assertIn("Expense", content)
        self.assertIn("Food", content)
        self.assertIn("Rent", content)


class RecommendationsTests(Epic5Base):
    """
    Covers user story 27 – intelligent recommendations to balance overspending.
    """

    def test_recommendations_focus_on_highest_expense_categories(self):
        from budget.reporting import recommendations

        recs = recommendations(self.budget.id, top_n=1)
        self.assertEqual(len(recs), 1)
        # Rent is largest expense (900 > 250)
        self.assertEqual(recs[0]["category"], "Rent")
        self.assertIn("Reduce Rent", recs[0]["suggestion"])


class WhatIfSimulationTests(Epic5Base):
    """
    Covers user story 28 – what-if simulations.
    """

    def test_what_if_endpoint_returns_projected_net(self):
        self.client.login(username="derrick", password="pass123")
        url = reverse("reports_what_if", args=[self.budget.id])

        # Plan: reduce Food by 50, increase income by 100
        payload = {
            "changes": [
                {"category": "Food", "delta": -50},
                {"category": "Side Income", "delta": 100},
            ]
        }
        resp = self.client.post(url, data=payload, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        # base net is 850 (from MonthlySummaryTests)
        self.assertEqual(Decimal(str(data["base"]["net"])), Decimal("850.00"))
        self.assertEqual(Decimal(str(data["delta"])), Decimal("50"))  # -50 + 100
        self.assertEqual(Decimal(str(data["projected_net"])), Decimal("900.00"))
