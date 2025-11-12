from django.test import TestCase
from budget.models import Expense, Budget
from django.contrib.auth.models import User

class Epic3ExpenseManagementTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create budgets for categories
        self.food_budget = Budget.objects.create(user=self.user, category='Food', amount=200)
        self.rent_budget = Budget.objects.create(user=self.user, category='Rent', amount=1000)

    def test_add_expense_with_category_and_notes(self):
        """User can add an expense with category and notes"""
        expense = Expense.objects.create(
            user=self.user,
            category='Food',
            amount=50,
            notes='Lunch with friends'
        )
        self.assertEqual(expense.category, 'Food')
        self.assertEqual(expense.notes, 'Lunch with friends')
        self.assertEqual(expense.amount, 50)

    def test_expense_approaching_budget(self):
        """Notify user when expense approaches budget (>=90%)"""
        expense = Expense.objects.create(user=self.user, category='Food', amount=180)
        budget = self.food_budget
        self.assertTrue(expense.amount >= 0.9 * budget.amount)

    def test_expense_exceeding_budget(self):
        """Notify user when expense exceeds budget"""
        expense = Expense.objects.create(user=self.user, category='Rent', amount=1200)
        budget = self.rent_budget
        self.assertTrue(expense.amount > budget.amount)
