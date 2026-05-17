from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from transactions.models import Category

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        cat_name = self.category.name if self.category else "Global"
        return f"Budget {cat_name} - {self.month}/{self.year}"

