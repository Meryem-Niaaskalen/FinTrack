from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SavingGoal
from .forms import SavingGoalForm, GoalContributionForm
from transactions.models import Transaction, Category
from django.contrib import messages
from datetime import date

@login_required
def goal_list(request):
    goals = SavingGoal.objects.filter(user=request.user)
    return render(request, 'goals/goal_list.html', {'goals': goals})

@login_required
def goal_contribution(request, pk):
    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalContributionForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account = form.cleaned_data['account']
            
            if account.balance >= amount:
                # 1. Update Goal
                goal.current_amount += amount
                was_completed = goal.is_completed
                if goal.current_amount >= goal.target_amount:
                    goal.is_completed = True
                goal.save()
                
                # 2. Create Transaction (Expense for savings)
                # Let's try to find an 'Épargne' category or create one
                category, _ = Category.objects.get_or_create(name='Épargne', type='expense')
                
                Transaction.objects.create(
                    user=request.user,
                    account=account,
                    category=category,
                    type='expense',
                    amount=amount,
                    description=f"Épargne pour : {goal.name}",
                    date=date.today()
                )
                
                # Note: Transaction.save() already handles account balance deduction
                
                # 3. Gamification
                request.user.profile.add_points(20, reason=f"Contribution à l'objectif : {goal.name}", request=request)
                if goal.is_completed and not was_completed:
                    request.user.profile.add_points(100, reason=f"Objectif atteint ! : {goal.name}", request=request)
                
                messages.success(request, f"{amount} MAD transférés avec succès vers '{goal.name}' !")
                return redirect('goal_list')
            else:
                messages.error(request, "Solde insuffisant sur le compte sélectionné.")
    else:
        form = GoalContributionForm(user=request.user)
    
    return render(request, 'goals/goal_form.html', {
        'form': form, 
        'title': f"Épargner pour {goal.name}",
        'is_contribution': True,
        'goal': goal
    })

@login_required
def goal_create(request):
    if request.method == 'POST':
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('goal_list')
    else:
        form = SavingGoalForm()
    return render(request, 'goals/goal_form.html', {'form': form, 'title': 'Créer un objectif'})

@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SavingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save()
            if goal.current_amount >= goal.target_amount and not goal.is_completed:
                goal.is_completed = True
                goal.save()
                request.user.profile.add_points(100, reason=f"Objectif atteint : {goal.name}", request=request)
            return redirect('goal_list')
    else:
        form = SavingGoalForm(instance=goal)
    return render(request, 'goals/goal_form.html', {'form': form, 'title': 'Modifier l\'objectif'})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('goal_list')
    return render(request, 'goals/goal_confirm_delete.html', {'goal': goal})
