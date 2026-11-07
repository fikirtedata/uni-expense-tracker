from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense, Category, Budget
from .forms import ExpenseForm, CategoryForm, BudgetForm

@login_required
def dashboard(request):
    if request.method == 'POST':
        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST, user=request.user)
            if form.is_valid():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('dashboard')
        elif 'add_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category = category_form.save(commit=False)
                category.user = request.user
                category.save()
                return redirect('dashboard')
        elif 'add_budget' in request.POST:
            budget_form = BudgetForm(request.POST, user=request.user)
            if budget_form.is_valid():
                cat = budget_form.cleaned_data['category']
                limit = budget_form.cleaned_data['monthly_limit']
                # Update if budget exists for this category, or create new
                Budget.objects.update_or_create(
                    user=request.user,
                    category=cat,
                    defaults={'monthly_limit': limit}
                )
                return redirect('dashboard')

    # Initialize empty forms
    form = ExpenseForm(user=request.user)
    category_form = CategoryForm()
    budget_form = BudgetForm(user=request.user)

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.filter(user=request.user)
    budgets = Budget.objects.filter(user=request.user)
    
    total_spent = sum(exp.amount for exp in expenses)

    # Calculate budget progress per category
    budget_progress = []
    for cat in categories:
        spent = expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        budget_obj = budgets.filter(category=cat).first()
        limit = budget_obj.monthly_limit if budget_obj else 0
        
        # Calculate percentage (capped at 100% for progress bar styling)
        if limit > 0:
            percentage = int((spent / limit) * 100)
            capped_percentage = min(percentage, 100)
        else:
            percentage = 0
            capped_percentage = 0

        # REMOVED: budget_progress.html = True (This caused the crash!)

        budget_progress.append({
            'category': cat.name,
            'spent': spent,
            'limit': limit,
            'percentage': percentage,
            'capped_percentage': capped_percentage,
            'is_over': spent > limit if limit > 0 else False
        })
    context = {
        'expenses': expenses,
        'categories': categories,
        'total_spent': total_spent,
        'form': form,
        'category_form': category_form,
        'budget_form': budget_form,
        'budget_progress': budget_progress,
    }
    return render(request, 'tracker/dashboard.html', context)
def delete_expense(request, pk):
    # Ensure the user can only delete their own expenses
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return redirect('dashboard')