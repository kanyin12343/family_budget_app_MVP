from django.shortcuts import render, redirect
from .models import Income, Expense
import json
import os

# Helper functions to handle per-user data
def get_user_file(username):
    return f"{username}_data.json"

def load_user_data(username):
    filename = get_user_file(username)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {"income": [], "expenses": [], "total_income": 0, "total_expense": 0, "balance": 0}

def save_user_data(username, data):
    filename = get_user_file(username)
    with open(filename, "w") as f:
        json.dump(data, f)

# -------------------------------------------
# LOGIN
# -------------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if username:
            request.session['username'] = username
            return redirect('dashboard')
    return render(request, "login.html")


# -------------------------------------------
# DASHBOARD (Shows totals)
# -------------------------------------------
def dashboard_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    user_data = load_user_data(username)

    context = {
        "username": username,
        "total_income": user_data["total_income"],
        "total_expense": user_data["total_expense"],
        "balance": user_data["balance"],
    }
    return render(request, "dashboard.html", context)


# -------------------------------------------
# ADD INCOME (EPIC 2)
# -------------------------------------------
def add_income_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    if request.method == "POST":
        source = request.POST.get("source")
        amount = request.POST.get("amount")
        contributor = request.POST.get("contributor")
        planned = request.POST.get("planned") == "on"
        date = request.POST.get("date")

        if source and amount:
            user_data = load_user_data(username)

            new_entry = {
                "id": len(user_data["income"]) + 1,
                "source": source,
                "amount": float(amount),
                "contributor": contributor,
                "planned": planned,
                "date": date
            }

            user_data["income"].append(new_entry)
            user_data["total_income"] += float(amount)
            user_data["balance"] = user_data["total_income"] - user_data["total_expense"]

            save_user_data(username, user_data)

            return redirect('dashboard')

    return render(request, "add_income.html", {"username": username})


# -------------------------------------------
# ADD EXPENSE
# -------------------------------------------
def add_expense_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    error_message = None
    category_value = ""
    amount_value = ""

    if request.method == "POST":
        category = request.POST.get("category")
        amount = request.POST.get("amount")

        # Keep values to refill the form
        category_value = category
        amount_value = amount

        if category and amount:
            try:
                amount_float = float(amount)
                total_income = sum(i.amount for i in Income.objects.all())
                total_expense = sum(e.amount for e in Expense.objects.all())

                if total_expense + amount_float > total_income:
                    error_message = "Error: Expense exceeds your available budget!"
                else:
                    Expense.objects.create(category=category, amount=amount_float)
                    return redirect('dashboard')
            except ValueError:
                error_message = "Invalid amount entered."

    context = {
        "username": username,
        "error_message": error_message,
        "category_value": category_value,
        "amount_value": amount_value,
    }
    return render(request, "add_expense.html", context)
            user_data = load_user_data(username)
            expense_item = {"category": category, "amount": float(amount)}
            user_data["expenses"].append(expense_item)
            user_data["total_expense"] += float(amount)
            user_data["balance"] = user_data["total_income"] - user_data["total_expense"]
            save_user_data(username, user_data)
            return redirect('dashboard')




# -------------------------------------------
# SUMMARY PAGE
# -------------------------------------------
def summary_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    user_data = load_user_data(username)

    context = {
        "username": username,
        "incomes": user_data["income"],
        "expenses": user_data["expenses"],
        "total_income": user_data["total_income"],
        "total_expense": user_data["total_expense"],
        "balance": user_data["balance"],
    }
    return render(request, "summary.html", context)


# =================================================================
#                   EPIC 2 — INCOME MANAGEMENT
# =================================================================

# -------------------------------------------
# VIEW INCOME LIST
# -------------------------------------------
def view_income(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user_data = load_user_data(username)
    return render(request, "view_income.html", {
        "username": username,
        "incomes": user_data["income"],
    })


# -------------------------------------------
# EDIT INCOME
# -------------------------------------------
def edit_income(request, income_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user_data = load_user_data(username)

    # Find entry
    income_item = next((i for i in user_data["income"] if i["id"] == income_id), None)
    if not income_item:
        return redirect('view_income')

    if request.method == "POST":
        income_item["source"] = request.POST.get("source")
        income_item["amount"] = float(request.POST.get("amount"))
        income_item["contributor"] = request.POST.get("contributor")
        income_item["planned"] = request.POST.get("planned") == "on"
        income_item["date"] = request.POST.get("date")

        # Recalculate totals
        user_data["total_income"] = sum(i["amount"] for i in user_data["income"])
        user_data["balance"] = user_data["total_income"] - user_data["total_expense"]

        save_user_data(username, user_data)
        return redirect('view_income')

    return render(request, "edit_income.html", {
        "username": username,
        "income": income_item,
    })


# -------------------------------------------
# DELETE INCOME
# -------------------------------------------
def delete_income(request, income_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user_data = load_user_data(username)

    user_data["income"] = [i for i in user_data["income"] if i["id"] != income_id]

    # Recalculate totals
    user_data["total_income"] = sum(i["amount"] for i in user_data["income"])
    user_data["balance"] = user_data["total_income"] - user_data["total_expense"]

    save_user_data(username, user_data)

    return redirect('view_income')
