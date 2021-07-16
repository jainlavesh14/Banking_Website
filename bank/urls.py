
from django.contrib import admin
from django.urls import path
from bank_app.views import about, add_customer, view_customers, more_info, contact, transfer, transaction_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', about, name = 'about'),
    path('add_customer/', add_customer, name = 'add_customer'),
    path('view_customers/', view_customers, name = "view_customers"),
    path('more_info/<str:email>', more_info, name = 'more_info'),
    path('contact/', contact, name = 'contact'),
    path('transfer/', transfer, name = 'transfer'),
    path('transaction_history/', transaction_history, name = 'transaction_history'),
]
