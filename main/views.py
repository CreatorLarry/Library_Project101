from django.shortcuts import render

from main.models import Book, Transaction


# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')


def books_in_store(request):
    books = Book.objects.all()
    return render(request, 'book_in_store.html', {'books': books})


def borrowed_books(request):
    borrowed = Transaction.objects.all()
    return render(request, 'borrowed_books.html', {'borrowed_books': borrowed})


def returned_books(request):
    return render(request, 'returned_books.html')


def book_fines(request):
    return render(request, 'book_fines.html')


def issue_book(request):
    return render(request, 'issue_book.html')