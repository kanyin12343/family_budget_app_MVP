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

# Simulated login (stores name in session)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if username:
            request.session['username'] = username
            return redirect('dashboard')
    return render(request, "login.html")

# Dashboard now shows user-specific data
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

# Add income to user-specific file
def add_income_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    if request.method == "POST":
        source = request.POST.get("source")
        amount = request.POST.get("amount")
        if source and amount:
            user_data = load_user_data(username)
            income_item = {"source": source, "amount": float(amount)}
            user_data["income"].append(income_item)
            user_data["total_income"] += float(amount)
            user_data["balance"] = user_data["total_income"] - user_data["total_expense"]
            save_user_data(username, user_data)
            return redirect('dashboard')

    return render(request, "add_income.html", {"username": username})

# Add expense to user-specific file
def add_expense_view(request):
    username = request.session.get('username', None)
    if not username:
        return redirect('login')

    if request.method == "POST":
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        if category and amount:
            user_data = load_user_data(username)
            expense_item = {"category": category, "amount": float(amount)}
            user_data["expenses"].append(expense_item)
            user_data["total_expense"] += float(amount)
            user_data["balance"] = user_data["total_income"] - user_data["total_expense"]
            save_user_data(username, user_data)
            return redirect('dashboard')

    return render(request, "add_expense.html", {"username": username})

# Optional: personalized summary view
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
