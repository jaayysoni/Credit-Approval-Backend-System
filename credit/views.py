from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Sum, F
from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta

from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer

# ==================================
# Dashboard View
# ==================================

def dashboard(request):
    return render(request, "dashboard.html")


# ==================================
# Helper Functions
# ==================================

def calculate_emi(principal, annual_rate, tenure_months):
    r_month = annual_rate / 12 / 100
    n = tenure_months

    if r_month == 0:
        return round(principal / n, 2)

    emi = principal * r_month * (1 + r_month) ** n / ((1 + r_month) ** n - 1)
    return round(emi, 2)


def calculate_credit_score(customer):
    loans = customer.loans.all()
    score = 50

    total_current_loans = loans.filter(is_active=True).aggregate(
        total=Sum("loan_amount")
    )["total"] or 0

    if total_current_loans > customer.approved_limit:
        return 0

    on_time_ratio = sum(l.emis_paid_on_time for l in loans) / max(len(loans), 1)
    score += on_time_ratio * 50

    score -= len(loans) * 5

    score -= sum(
        1 for l in loans
        if l.start_date and l.start_date.year == date.today().year
    ) * 5

    total_emi = loans.filter(is_active=True).aggregate(
        total=Sum("monthly_repayment")
    )["total"] or 0

    if total_emi > 0.5 * customer.monthly_salary:
        score = min(score, 10)

    return max(0, min(100, score))


def check_eligibility_logic(customer, loan_amount, interest_rate, tenure):
    loans = customer.loans.all()

    # Rule 1: If total current loans > approved_limit → reject
    total_current_loans = loans.filter(is_active=True).aggregate(
        total=Sum("loan_amount")
    )["total"] or 0

    if total_current_loans > customer.approved_limit:
        return False, interest_rate, 0

    # Rule 2: If total EMI > 50% salary → reject
    total_emi = loans.filter(is_active=True).aggregate(
        total=Sum("monthly_repayment")
    )["total"] or 0

    if total_emi > 0.5 * customer.monthly_salary:
        return False, interest_rate, 0

    # ---- Credit Score Calculation ----
    score = 50

    if loans.exists():
        on_time_ratio = sum(l.emis_paid_on_time for l in loans) / len(loans)
        score += on_time_ratio * 50

    score -= loans.count() * 5

    score -= sum(
        1 for l in loans
        if l.start_date.year == date.today().year
    ) * 5

    score = max(0, min(100, score))

    # ---- Approval Slabs ----
    corrected_rate = interest_rate
    approved = False

    if score > 50:
        approved = True
    elif 50 >= score > 30:
        corrected_rate = max(interest_rate, 12)
        approved = True
    elif 30 >= score > 10:
        corrected_rate = max(interest_rate, 16)
        approved = True
    else:
        approved = False

    if not approved:
        return False, corrected_rate, 0

    monthly_installment = calculate_emi(
        loan_amount,
        corrected_rate,
        tenure
    )

    return True, corrected_rate, monthly_installment


# ==================================
# Customer ViewSet
# ==================================

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=["get"])
    def total_debt(self, request, pk=None):
        customer = self.get_object()
        total = customer.loans.filter(is_active=True).aggregate(
            total=Sum("loan_amount")
        )["total"] or 0
        return Response({
            "customer_id": customer.customer_id,
            "total_debt": total
        })


# ==================================
# Loan ViewSet
# ==================================

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    @action(detail=False, methods=["get"])
    def late_loans(self, request):
        late = Loan.objects.filter(emis_paid_on_time__lt=F("tenure"))
        serializer = self.get_serializer(late, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active_loans(self, request):
        active = Loan.objects.filter(is_active=True)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)


# ==================================
# API Endpoints
# ==================================

@api_view(["POST"])
def register_customer(request):
    try:
        data = request.data
        monthly_salary = float(data.get("monthly_income"))
        approved_limit = round(36 * monthly_salary / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            age=int(data.get("age")),
            phone_number=data.get("phone_number"),
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
            current_debt=0
        )

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def check_eligibility(request):
    try:
        data = request.data

        customer_id = data.get("customer_id")
        loan_amount = data.get("loan_amount")
        interest_rate = data.get("interest_rate")
        tenure = data.get("tenure")

        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return Response({"error": "All fields are required"}, status=400)

        try:
            customer_id = int(customer_id)
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
        except ValueError:
            return Response({"error": "Invalid data type"}, status=400)

        customer = get_object_or_404(Customer, customer_id=customer_id)

        approved, corrected_rate, monthly_installment = check_eligibility_logic(
            customer, loan_amount, interest_rate, tenure
        )

        return Response({
            "customer_id": customer.customer_id,
            "approval": approved,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_rate,
            "tenure": tenure,
            "monthly_installment": round(monthly_installment, 2)
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
def create_loan(request):
    data = request.data

    # Validate input
    customer_id = data.get("customer_id")
    loan_amount = data.get("loan_amount")
    interest_rate = data.get("interest_rate")
    tenure = data.get("tenure")

    if not all([customer_id, loan_amount, interest_rate, tenure]):
        return Response({"error": "All fields are required"}, status=400)

    try:
        customer_id = int(customer_id)
        loan_amount = float(loan_amount)
        interest_rate = float(interest_rate)
        tenure = int(tenure)
    except ValueError:
        return Response({"error": "Invalid data type"}, status=400)

    # Get customer
    customer = get_object_or_404(Customer, customer_id=customer_id)

    # Check eligibility
    approved, corrected_rate, monthly_installment = check_eligibility_logic(
        customer, loan_amount, interest_rate, tenure
    )

    if not approved:
        return Response({
            "loan_approved": False,
            "message": "Loan not approved due to credit score or limits"
        }, status=400)

    # Generate loan_id
    last_loan = Loan.objects.order_by("-loan_id").first()
    loan_id = (last_loan.loan_id + 1) if last_loan else 1

    # Create loan
    loan = Loan.objects.create(
        loan_id=loan_id,
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=round(corrected_rate, 2),
        monthly_repayment=round(monthly_installment, 2),
        emis_paid_on_time=0,
        is_active=True,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30 * tenure)
    )

    # Update customer debt
    customer.current_debt += loan_amount
    customer.save(update_fields=["current_debt"])

    return Response({
        "loan_id": loan.loan_id,
        "loan_approved": True,
        "loan_amount": loan.loan_amount,
        "tenure": loan.tenure,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "start_date": loan.start_date,
        "end_date": loan.end_date
    })


@api_view(["GET"])
def view_loan(request, loan_id):
    loan = get_object_or_404(Loan, loan_id=loan_id)
    return Response({
        "loan_id": loan.loan_id,
        "customer_id": loan.customer.customer_id,
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "tenure": loan.tenure
    })


@api_view(["GET"])
def view_loans_by_customer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    loans = customer.loans.all()

    result = [
        {
            "loan_id": l.loan_id,
            "loan_amount": l.loan_amount,
            "interest_rate": l.interest_rate,
            "monthly_installment": l.monthly_repayment,
            "repayments_left": max(0, l.tenure - l.emis_paid_on_time)
        }
        for l in loans
    ]
    return Response(result)