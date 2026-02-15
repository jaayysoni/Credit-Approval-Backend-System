from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
from .views import (
    CustomerViewSet,
    LoanViewSet,
    register_customer,
    check_eligibility,
    create_loan,
    view_loan,
    view_loans_by_customer,
)

# ==============================
# Router for ViewSets
# ==============================
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'loans', LoanViewSet, basename='loan')

# ==============================
# URL Patterns
# ==============================
urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),

    # Custom function-based endpoints
    path('register/', register_customer, name='register_customer'),
    path('eligibility/', check_eligibility, name='check_eligibility'),
    path('create-loan/', create_loan, name='create_loan'),
    path('loan/<int:loan_id>/', view_loan, name='view_loan'),
    path('customer/<int:customer_id>/loans/', view_loans_by_customer, name='view_loans_by_customer'),
    path("", views.dashboard, name="dashboard"),
]