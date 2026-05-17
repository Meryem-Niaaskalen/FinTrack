from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Sum, Q, Count, Avg
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import login
from django.contrib import messages

from .forms import UserRegisterForm
from accounts.models import Account
from transactions.models import Transaction
from budgets.models import Budget
from goals.models import SavingGoal
from gamification.models import UserBadge, Badge
from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username} ! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def login_success(request):
    """Redirige les utilisateurs vers le bon portail après connexion."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('dashboard')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
        
    user = request.user
    
    # Profile (Gamification)
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'first_name': user.first_name or user.username,
            'last_name': user.last_name or "",
        }
    )
    
    # Badges
    badges = UserBadge.objects.filter(user=user).select_related('badge')

    # Objectifs d'épargne
    goals = SavingGoal.objects.filter(user=user)

    # Comptes
    accounts = Account.objects.filter(user=user)

    # Solde global
    total_balance = accounts.aggregate(
        total=Sum('balance')
    )['total'] or 0

    # Revenus et dépenses
    total_income = Transaction.objects.filter(
        user=user, type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expense = Transaction.objects.filter(
        user=user, type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Transactions récentes
    transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date')[:5]

    # Budgets de l'année
    today = date.today()
    budgets = Budget.objects.filter(
        user=user,
        year=today.year
    ).order_by('month')

    budgets_data = []
    for budget in budgets:
        # Calculer les dépenses seulement si c'est le mois en cours ou passé
        spent = 0
        if budget.month <= today.month:
            if budget.category:
                spent = Transaction.objects.filter(
                    user=user,
                    type='expense',
                    category=budget.category,
                    date__month=budget.month,
                    date__year=budget.year
                ).aggregate(total=Sum('amount'))['total'] or 0
            else:
                spent = Transaction.objects.filter(
                    user=user,
                    type='expense',
                    date__month=budget.month,
                    date__year=budget.year
                ).aggregate(total=Sum('amount'))['total'] or 0
        
        exceeded = spent > budget.amount
        is_future = budget.month > today.month
        
        budgets_data.append({
            'budget': budget,
            'spent': spent,
            'exceeded': exceeded,
            'is_future': is_future,
            'month_name': budget.get_month_display() if hasattr(budget, 'get_month_display') else f"Mois {budget.month}"
        })

    # Données pour le graphique des dépenses par catégorie
    category_expenses = Transaction.objects.filter(
        user=user, type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    chart_categories = [item['category__name'] or "Autre" for item in category_expenses]
    chart_data = [float(item['total']) for item in category_expenses]

    context = {
        'profile': profile,
        'badges': badges,
        'goals': goals,
        'accounts': accounts,
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'transactions': transactions,
        'budgets_data': budgets_data,
        'chart_categories': chart_categories,
        'chart_data': chart_data,
    }

    return render(request, 'users/dashboard.html', context)


@login_required
def analytics(request):
    user = request.user
    today = date.today()
    
    # 1. Monthly Trends (Last 6 Months)
    months_labels = []
    income_trends = []
    expense_trends = []
    
    for i in range(5, -1, -1):
        target_date = today - relativedelta(months=i)
        month_name = target_date.strftime('%b %Y')
        months_labels.append(month_name)
        
        inc = Transaction.objects.filter(
            user=user, type='income', 
            date__month=target_date.month, 
            date__year=target_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        exp = Transaction.objects.filter(
            user=user, type='expense', 
            date__month=target_date.month, 
            date__year=target_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        income_trends.append(float(inc))
        expense_trends.append(float(exp))

    # 2. Category Breakdown (Current Month)
    category_expenses = Transaction.objects.filter(
        user=user, type='expense',
        date__month=today.month,
        date__year=today.year
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    cat_labels = [item['category__name'] or "Autre" for item in category_expenses]
    cat_data = [float(item['total']) for item in category_expenses]

    # 3. Savings Rate
    total_inc = sum(income_trends)
    total_exp = sum(expense_trends)
    savings = total_inc - total_exp
    savings_rate = (savings / total_inc * 100) if total_inc > 0 else 0

    context = {
        'months_labels': months_labels,
        'income_trends': income_trends,
        'expense_trends': expense_trends,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'savings_rate': round(savings_rate, 1),
        'total_savings': savings,
    }
    return render(request, 'users/analytics.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='dashboard')
def admin_dashboard(request):
    # Global User Stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    # Financial Stats (Global)
    total_global_balance = Account.objects.aggregate(Sum('balance'))['balance__sum'] or 0
    total_global_income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_global_expense = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Gamification Stats
    avg_level = Profile.objects.aggregate(Avg('level'))['level__avg'] or 1
    total_badges_awarded = UserBadge.objects.count()

    # Chart 1: Users by Level
    levels_data = Profile.objects.values('level').annotate(count=Count('id')).order_by('level')
    level_labels = [f"Niveau {item['level']}" for item in levels_data]
    level_counts = [item['count'] for item in levels_data]

    # Chart 2: Recent Global Transactions (last 6 months overview)
    # For simplicity, let's just do a breakdown of Income vs Expense
    type_data = Transaction.objects.values('type').annotate(total=Sum('amount'))
    type_labels = ["Revenus", "Dépenses"]
    type_values = [0, 0]
    for item in type_data:
        if item['type'] == 'income':
            type_values[0] = float(item['total'])
        else:
            type_values[1] = float(item['total'])

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_global_balance': total_global_balance,
        'total_global_income': total_global_income,
        'total_global_expense': total_global_expense,
        'avg_level': round(avg_level, 1),
        'total_badges_awarded': total_badges_awarded,
        'level_labels': level_labels,
        'level_counts': level_counts,
        'type_labels': type_labels,
        'type_values': type_values,
    }

    return render(request, 'users/admin_dashboard.html', context)
