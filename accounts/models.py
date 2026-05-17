
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('bank', 'Compte bancaire'),
        ('card', 'Carte bancaire'),
        ('wallet', 'Portefeuille'),
        ('saving', 'Compte épargne'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
