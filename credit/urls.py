from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'loans', views.LoanViewSet, basename='loan')

urlpatterns = [
    path('', include(router.urls)),

    # API endpoints
    path('register/', views.register_customer, name='register_customer'),
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('loan/<int:loan_id>/', views.view_loan, name='view_loan'),
    path('customer/<int:customer_id>/loans/', views.view_loans_by_customer, name='view_loans_by_customer'),
]