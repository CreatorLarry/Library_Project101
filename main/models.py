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
        odering = ['reader_no']
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
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    transaction_date = models.DateField()
    transaction_time = models.TimeField()