from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class SavingGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Objectif d'épargne")
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.target_amount}"

