from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm

@login_required
def dashboard(request):
    if request.method == 'POST':
        # Check which form was submitted using a hidden/name identifier
        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST, user=request.user)
            if form.is_valid():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('dashboard')
            category_form = CategoryForm(user=request.user) # Keep empty form ready
        elif 'add_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category = category_form.save(commit=False)
                category.user = request.user
                category.save()
                return redirect('dashboard')
            form = ExpenseForm(user=request.user) # Keep empty form ready
    else:
        form = ExpenseForm(user=request.user)
        category_form = CategoryForm()

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.filter(user=request.user)
    total_spent = sum(exp.amount for exp in expenses)

    context = {
        'expenses': expenses,
        'categories': categories,
        'total_spent': total_spent,
        'form': form,
        'category_form': category_form,
    }
    return render(request, 'tracker/dashboard.html', context)