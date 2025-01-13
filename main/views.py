import json
from datetime import timedelta, date

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient

from main.models import Book, Transaction, Reader, Payment


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
    transactions = Transaction.objects.all()
    fines = [t for t in transactions if t.total_fine > 0]
    return render(request, 'book_fines.html', {'fines': fines})


def issue_book(request, id):
    book = Book.objects.get(pk=1)
    readers = Reader.objects.all()
    if request.method == 'POST':
        reader_id = request.POST['reader_id']
        reader = Reader.objects.get(pk=reader_id)
        expected_return_date = date.today() + timedelta(days=7)
        transaction = Transaction.objects.create(
            book=book,
            reader=reader,
            expected_return_date=expected_return_date,
            status='BORROWED',  # Explicitly setting the status
        )
        transaction.save()

        messages.success(request, f'Book: {book.title} borrowed successfully by {reader.name}')
        return redirect('books_in_store')

    return render(request, 'issue_book.html', {'book': book, 'readers': readers})


def return_book(request, id):
    transaction = Transaction.objects.get(pk=id)
    transaction.return_date = date.today()
    transaction.status = 'RETURNED'
    transaction.save()
    messages.success(request, f'Book: {transaction.book.title} returned successfully')
    if transaction.total_fine > 0:
        messages.warning(request,
                         f'Book: {transaction.book.title} has incurred a fine of Ksh. {transaction.total_fine}')

    # transaction.delete()
    return redirect('books_in_store')


def pay_overdue(request, id):
    transaction = Transaction.objects.get(pk=id)
    total = transaction.total_fine
    phone = transaction.reader.phone

    def trigger(request):
        cl = MpesaClient()
        phone_number = '0723740215'
        amount = 1
        account_reference = transaction.reader.reader_no
        transaction_desc = 'Fines'
        callback_url = 'https://mature-octopus-causal.ngrok-free.app/handle/payment/transactions'
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        if response.response_code == "0":
            payment = Payment.objects.create(transaction=transaction,
                                             merchant_request_id=response.merchant_request_id,
                                             checkout_request_id=response.checkout_request_id,
                                             amount=amount)
            payment.save()

    messages.success(request, f'Trigger has been sent successfully.')
    return redirect('book_fines')

@csrf_exempt
def callback(request):
    resp = json.loads(request.body)
    data = resp['Body']['stkCallback']
    if data["ResultCode"] == "0":
        m_id = data["MerchantRequestID"]
        c_id = data["CheckoutRequestID"]
        code = ""
        amount = ""
        item = data["CallbackMetadata"]["Item"]
        for i in item:
            name = i["Name"]
            if name == "MpesaReceiptNumber":
                code = i["Value"]

            if name == "Amount":
                amount = i["Value"]


        transaction = Transaction.objects.create(merchant_request_id=m_id, checkout_request_id=c_id,)
        transaction.code = code
        transaction.amount = amount
        transaction.status = 'COMPLETED'
        transaction.save()
    return HttpResponse("OK")