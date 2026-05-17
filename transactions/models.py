from django.db import models

from django.contrib.auth.models import User
from accounts.models import Account
# Create your models here.

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Revenu'),
        ('expense', 'Dépense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Revenu'),
        ('expense', 'Dépense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        if self.pk:
            # Revert old balance if editing
            old_transaction = Transaction.objects.get(pk=self.pk)
            if old_transaction.type == 'income':
                old_transaction.account.balance -= old_transaction.amount
            else:
                old_transaction.account.balance += old_transaction.amount
            old_transaction.account.save()

        # Apply new balance
        if self.type == 'income':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Revert balance before deleting
        if self.type == 'income':
            self.account.balance -= self.amount
        else:
            self.account.balance += self.amount
        self.account.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.amount}"


class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transfers_out')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transfers_in')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        if self.pk:
            # Revert old balance
            old_transfer = Transfer.objects.get(pk=self.pk)
            old_transfer.from_account.balance += old_transfer.amount
            old_transfer.to_account.balance -= old_transfer.amount
            old_transfer.from_account.save()
            old_transfer.to_account.save()

        # Apply new balance
        self.from_account.balance -= self.amount
        self.to_account.balance += self.amount
        self.from_account.save()
        self.to_account.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.from_account.balance += self.amount
        self.to_account.balance -= self.amount
        self.from_account.save()
        self.to_account.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Transfer {self.amount} from {self.from_account} to {self.to_account}"


class RecurringTransaction(models.Model):
    FREQUENCIES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=[('income', 'Revenu'), ('expense', 'Dépense')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES)
    start_date = models.DateField()
    next_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.description} ({self.get_frequency_display()})"

