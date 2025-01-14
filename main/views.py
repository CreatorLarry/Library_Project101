import json
from datetime import timedelta, date, datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient

from main.models import Book, Transaction, Reader, Payment


@login_required  # Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def books_in_store(request):
    books = Book.objects.all()
    return render(request, 'book_in_store.html', {'books': books})


@login_required
def borrowed_books(request):
    borrowed = Transaction.objects.filter(status='BORROWED')
    return render(request, 'borrowed_books.html', {'borrowed_books': borrowed})


@login_required
def returned_books(request):
    return render(request, 'returned_books.html')


@login_required
def book_fines(request):
    transactions = Transaction.objects.all()
    fines = [t for t in transactions if t.total_fine > 0]
    return render(request, 'book_fines.html', {'fines': fines})


@login_required
def issue_book(request, id):
    book = get_object_or_404(Book, pk=id)
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


@login_required
def return_book(request, id):
    transaction = get_object_or_404(Transaction, pk=id)
    transaction.return_date = date.today()
    transaction.status = 'RETURNED'
    transaction.save()
    messages.success(request, f'Book: {transaction.book.title} returned successfully')
    if transaction.total_fine > 0:
        messages.warning(request,
                         f'Book: {transaction.book.title} has incurred a fine of Ksh. {transaction.total_fine}')

    # transaction.delete()
    return redirect('books_in_store')


@login_required
def pay_overdue(request, id):
    transaction = get_object_or_404(Transaction, pk=id)
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

        transaction = Transaction.objects.create(merchant_request_id=m_id, checkout_request_id=c_id, )
        transaction.code = code
        transaction.amount = amount
        transaction.status = 'COMPLETED'
        transaction.save()
    return HttpResponse("OK")


@login_required
def pie_chart(request):
    transactions = Transaction.objects.filter(created_at__year=2024)
    returned = transactions.filter(status='RETURNED').count()
    lost = transactions.filter(status='LOST').count()
    borrowed = transactions.filter(status='BORROWED').count()

    return JsonResponse({
        "title": "Transactions Grouped By Status",
        "data": {
            "labels": ["Returned", "Borrowed", "Lost"],
            "datasets": [{
                "data": [returned, lost, borrowed],
                "backgroundColor": ['#4e73df', '#1cc88a', '#36b9cc'],
                "hoverBackgroundColor": ['#2e59d9', '#17a673', '#2c9faf'],
                "hoverBorderColor": "rgba(234, 236, 244, 1)",
            }],
        },
    })


@login_required
def line_chart(request):
    transactions = Transaction.objects.filter(created_at__year=2024)
    grouped = transactions.annotate(month=TruncMonth('created_at')).values('month').annotate(
        count=Count('id')).order_by('month')
    numbers = []
    months = []

    for i in grouped:
        numbers.append(i['count'])
        months.append(i['month'].strftime('%b'))
    return JsonResponse({
        "title": "Transactions Grouped By Month",
        "data": {
            "labels": months,
            "datasets": [{
                "label": "Count",
                "lineTension": 0.3,
                "backgroundColor": "rgba(78, 115, 223, 0.05)",
                "borderColor": "rgba(78, 115, 223, 1)",
                "pointRadius": 3,
                "pointBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointBorderColor": "rgba(78, 115, 223, 1)",
                "pointHoverRadius": 3,
                "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
                "pointHitRadius": 10,
                "pointBorderWidth": 2,
                "data": numbers,
            }],
        }
    })


# ctrl + F5 - Hard refreshing of a page
@login_required
def bar_chart(request):
    transactions = Transaction.objects.filter(created_at__year=2024)
    grouped = transactions.annotate(month=TruncMonth('created_at')).values('month').annotate(
        count=Count('id')).order_by('month')
    numbers = []
    months = []

    for i in grouped:
        numbers.append(i['count'])
        months.append(i['month'].strftime('%b'))
    return JsonResponse({
        "title": "Transactions Grouped By Month",
        "data": {
            "labels": months,
            "datasets": [{
                "label": "Total",
                "backgroundColor": "#4e73df",
                "hoverBackgroundColor": "#2e59d9",
                "borderColor": "#4e73df",
                "data": numbers,
            }],
        },
    })


def login_page(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('dashboard')
        else:
            messages.warning(request, "Invalid username or password.")

    return render(request, 'login.html')


@login_required
def logout_page(request):
    logout(request)
    return redirect('login')


@login_required
@permission_required("main.lost_book", raise_exception=True)
def lost_book(request, id):
    transactions = Transaction.objects.get(id=id)
    transactions.status = "LOST"
    transactions.return_date = datetime.today()
    transactions.save()
    messages.error(request, 'Book registered as lost')
    return redirect('borrowed_books')
