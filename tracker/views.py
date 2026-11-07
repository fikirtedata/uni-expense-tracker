from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense, Category, Budget

@login_required
def dashboard(request):
    # Fetch only the expenses and categories belonging to the currently logged-in user
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.filter(user=request.user)
    
    # Calculate the total amount spent
    total_spent = sum(exp.amount for exp in expenses)

    context = {
        'expenses': expenses,
        'categories': categories,
        'total_spent': total_spent,
    }
    return render(request, 'tracker/dashboard.html', context)