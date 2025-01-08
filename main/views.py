from django.shortcuts import render

from main.models import Book, Transaction, Reader


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


def issue_book(request, id):
    book = Book.objects.get(pk=1)
    readers = Reader.objects.all()
    return render(request, 'issue_book.html', {'book': book, 'readers': readers})