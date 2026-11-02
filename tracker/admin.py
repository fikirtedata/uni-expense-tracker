from django.contrib import admin

# Register your models here.
from .models import Category, Expense, Budget

admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Budget)