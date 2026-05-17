from django import forms
from .models import Budget
from transactions.models import Category
import datetime

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.Select(choices=[(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)], attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Category is optional (for global budget)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Global (Toutes catégories)"
        self.fields['category'].queryset = Category.objects.filter(type='expense')

        if not self.initial.get('year'):
            self.initial['year'] = datetime.date.today().year
        if not self.initial.get('month'):
            self.initial['month'] = datetime.date.today().month
