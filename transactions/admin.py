from django.contrib import admin
from .models import Category, Transaction
# Register your models here.

admin.site.register(Category)
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'date', 'account')
    list_filter = ('type', 'date')
    search_fields = ('description',)