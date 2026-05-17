from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction, Transfer, Category, RecurringTransaction
from .forms import TransactionForm, TransferForm, RecurringTransactionForm
from datetime import date
from dateutil.relativedelta import relativedelta
import csv
from django.http import HttpResponse

def process_recurring_transactions(user):
    today = date.today()
    recurring = RecurringTransaction.objects.filter(user=user, is_active=True, next_date__lte=today)
    
    for rec in recurring:
        while rec.next_date <= today:
            # Create the actual transaction
            Transaction.objects.create(
                user=user,
                account=rec.account,
                category=rec.category,
                type=rec.type,
                amount=rec.amount,
                description=f"[Récurrent] {rec.description}",
                date=rec.next_date
            )
            
            # Update next_date based on frequency
            if rec.frequency == 'daily':
                rec.next_date += relativedelta(days=1)
            elif rec.frequency == 'weekly':
                rec.next_date += relativedelta(weeks=1)
            elif rec.frequency == 'monthly':
                rec.next_date += relativedelta(months=1)
            elif rec.frequency == 'yearly':
                rec.next_date += relativedelta(years=1)
        
        rec.save()

@login_required
def transaction_list(request):
    process_recurring_transactions(request.user)
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = Transaction.objects.filter(user=request.user)

    if query:
        transactions = transactions.filter(description__icontains=query)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    transactions = transactions.order_by('-date')
    transfers = Transfer.objects.filter(user=request.user).order_by('-date')
    recurring_transactions = RecurringTransaction.objects.filter(user=request.user)
    
    categories = Category.objects.all()

    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'transfers': transfers,
        'recurring_transactions': recurring_transactions,
        'categories': categories
    })

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            
            request.user.profile.add_points(10, reason="Nouvelle transaction ajoutée", request=request)
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    categories = Category.objects.all()
    return render(request, 'transactions/transaction_form.html', {
        'form': form, 
        'title': 'Ajouter une transaction',
        'categories': categories
    })

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    categories = Category.objects.all()
    return render(request, 'transactions/transaction_form.html', {
        'form': form, 
        'title': 'Modifier la transaction',
        'categories': categories
    })

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})

# Transfer Views
@login_required
def transfer_create(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.user = request.user
            transfer.save()
            request.user.profile.add_points(15, reason="Virement entre comptes effectué", request=request)
            return redirect('transaction_list')
    else:
        form = TransferForm(user=request.user)
    return render(request, 'transactions/transaction_form.html', {'form': form, 'title': 'Effectuer un virement'})

@login_required
def transfer_delete(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk, user=request.user)
    if request.method == 'POST':
        transfer.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transfer, 'is_transfer': True})

# Recurring Transaction Views
@login_required
def recurring_create(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            if not recurring.next_date:
                recurring.next_date = recurring.start_date
            recurring.save()
            return redirect('transaction_list')
    else:
        form = RecurringTransactionForm(user=request.user)
    
    categories = Category.objects.all()
    return render(request, 'transactions/transaction_form.html', {
        'form': form, 
        'title': 'Planifier une transaction récurrente',
        'categories': categories
    })

@login_required
def recurring_delete(request, pk):
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    if request.method == 'POST':
        recurring.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': recurring})

@login_required
def export_transactions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_fintrack.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Categorie', 'Compte', 'Description', 'Montant'])

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    for t in transactions:
        writer.writerow([t.date, t.get_type_display(), t.category.name if t.category else '', t.account.name, t.description, t.amount])

    return response
