from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# -----------------------------
# DRF Routers for Customer & Loan
# -----------------------------
router = DefaultRouter()
router.register(r"api/customers", views.CustomerViewSet, basename="customer")
router.register(r"api/loans", views.LoanViewSet, basename="loan")

# -----------------------------
# URL Patterns (API-only)
# -----------------------------
urlpatterns = [
    # ----- Custom API endpoints -----
    path("api/register/", views.register_customer, name="api-register"),
    path("api/check-eligibility/", views.check_eligibility, name="api-check-eligibility"),
    path("api/create-loan/", views.create_loan, name="api-create-loan"),
    path("api/view-loan/<int:loan_id>/", views.view_loan, name="api-view-loan"),
    path("api/view-loans/<int:customer_id>/", views.view_loans_by_customer, name="api-view-loans-by-customer"),

    # ----- Standard CRUD endpoints via DRF router -----
    path("", include(router.urls)),
]