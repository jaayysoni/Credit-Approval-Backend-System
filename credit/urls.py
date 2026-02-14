from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("customers/", views.customer_management_page, name="customer-management"),
    path("loans/", views.loan_management_page, name="loan-management"),
]