from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ============================================================
# Existing Models (Income / Expense)
# ============================================================

class Income(models.Model):
    source = models.CharField(max_length=100)
    amount = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.source} - ${self.amount:.2f}"


class Expense(models.Model):
    """
    Expense model used by:
      - Existing app features
      - Tests in budget.tests.Expense* classes
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
        null=True,      # allow existing rows without a user
        blank=True,
    )
    category = models.CharField(max_length=100)
    amount = models.FloatField()

    note = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    recurring = models.BooleanField(default=False)

    # keep original field for backward compatibility
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.category} - ${self.amount:.2f}"


# ============================================================
# Epic 5 Models (Budget / Category / Transaction)
# ============================================================

class Budget(models.Model):
    """
    A named budget owned by a user.
    Used by Epic 5 tests for summaries & reports.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Category(models.Model):
    """
    A spending category tied to a specific budget.
    Example: Food, Rent, Misc.
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.budget.name})"


class Transaction(models.Model):
    """
    Positive amount = income
    Negative amount = expense
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} {self.description} {self.amount}"
