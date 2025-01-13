from datetime import datetime, date

from django.db import models


# Create your models here.
# Reader Model
class Reader(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    reader_no = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name} - {self.reader_no}'

    # class for more info
    class Meta:
        verbose_name = 'Reader'
        verbose_name_plural = 'Readers'
        ordering = ['reader_no']
        db_table = 'readers'


# book models
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    # pages = models.IntegerField()
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f'{self.title} - {self.isbn}'

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['isbn']
        db_table = 'books'


# Transactions
class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='transactions')
    status = models.CharField(
        max_length=10,
        choices=[
            ('BORROWED', 'Borrowed'),
            ('RETURNED', 'Returned'),
        ],
        default='BORROWED',
    )
    # Borrowed returned or lost
    expected_return_date = models.DateField()
    return_date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.book} - {self.reader}'

    @property
    def total_fine(self):
        if self.return_date and self.expected_return_date and self.return_date > self.expected_return_date:
            amount = (self.return_date - self.expected_return_date).days * 20
            return amount
        return 0

    @property
    def overdue_days(self):
        if self.return_date and self.expected_return_date and self.return_date > self.expected_return_date:
            days = (self.return_date - self.expected_return_date).days
            return days
        return 0

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        db_table = 'transactions'


# Payments
class Payment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    code = models.CharField(max_length=30, null=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        db_table = 'payments'

    def __str__(self):
        return f'{self.merchant_request_id} - {self.code} - {self.amount}'

# ALTER DATABASE `databasename` CHARACTER SET utf8;
