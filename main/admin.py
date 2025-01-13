from django.contrib import admin

from main.models import Reader, Book, Transaction, Payment


# Register your models here.
admin.site.site_header = 'BookVerse MIS'
admin.site.site_title = 'Manage Library MIS'


class ReaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'reader_no']
    search_fields = ['name', 'email', 'phone', 'reader_no']
    list_per_page = 25

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year', 'isbn', 'subject']
    search_fields = ['title', 'author', 'year', 'isbn', 'subject']
    list_per_page = 25

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['book', 'reader', 'status', 'expected_return_date']
    search_fields = ['book', 'reader', 'status', 'expected_return_date']
    list_per_page = 25

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'code', 'status', 'amount', 'created_at']
    search_fields = ['transaction', 'code', 'status', 'amount', 'created_at']
    list_per_page = 25


admin.site.register(Reader,ReaderAdmin)
admin.site.register(Book,BookAdmin)
admin.site.register(Transaction,TransactionAdmin)
admin.site.register(Payment,PaymentAdmin)