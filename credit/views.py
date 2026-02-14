from django.shortcuts import render

def index(request):
    """
    Home page → Customer Management
    """
    return render(request, "customer_management.html")


def customer_management_page(request):
    return render(request, "customer_management.html")


def loan_management_page(request):
    return render(request, "loan_management.html")