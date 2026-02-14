from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from datetime import date, timedelta

# ==============================
# Helper Functions
# ==============================
def calculate_emi(principal, annual_rate, tenure_months):
    """EMI formula using compound interest"""
    r_month = annual_rate / 12 / 100
    n = tenure_months
    if r_month == 0:
        return round(principal / n, 2)
    emi = principal * r_month * (1 + r_month) ** n / ((1 + r_month) ** n - 1)
    return round(emi, 2)


def calculate_credit_score(customer):
    """Simplified credit score based on past loans and current debt"""
    loans = customer.loans.all()
    score = 50

    # Total current loans
    total_current_loans = loans.filter(is_active=True).aggregate(total=Sum("loan_amount"))["total"] or 0
    if total_current_loans > customer.approved_limit:
        return 0

    # On-time repayment ratio
    on_time_ratio = sum(l.emis_paid_on_time for l in loans) / max(len(loans), 1)
    score += on_time_ratio * 50

    # Penalty for number of loans
    score -= len(loans) * 5

    # Penalty for loans started this year
    score -= sum(1 for l in loans if l.start_date and l.start_date.year == date.today().year) * 5

    # Penalty if EMI burden too high
    total_emi = loans.filter(is_active=True).aggregate(total=Sum("monthly_repayment"))["total"] or 0
    if total_emi > 0.5 * customer.monthly_salary:
        score = min(score, 10)

    return max(0, min(100, score))


def check_eligibility_logic(customer, loan_amount, interest_rate, tenure):
    """Check eligibility and adjust interest rate if needed"""
    score = calculate_credit_score(customer)
    corrected_rate = interest_rate
    approved = False

    if score > 50:
        approved = True
    elif 30 < score <= 50:
        corrected_rate = max(interest_rate, 12)
        approved = True
    elif 10 < score <= 30:
        corrected_rate = max(interest_rate, 16)
        approved = True
    else:
        approved = False

    monthly_installment = calculate_emi(loan_amount, corrected_rate, tenure)
    return approved, corrected_rate, monthly_installment


# ==============================
# Customer ViewSet
# ==============================
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=["get"])
    def total_debt(self, request, pk=None):
        """Get total current debt for a customer"""
        customer = self.get_object()
        total = customer.loans.filter(is_active=True).aggregate(
            total=Sum("loan_amount")
        )["total"] or 0
        return Response({"customer_id": customer.customer_id, "total_debt": total})


# ==============================
# Loan ViewSet
# ==============================
class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    @action(detail=False, methods=["get"])
    def late_loans(self, request):
        """List loans where EMIs paid are less than tenure"""
        late = Loan.objects.filter(emis_paid_on_time__lt=F("tenure"))
        serializer = self.get_serializer(late, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active_loans(self, request):
        """List all active loans"""
        active = Loan.objects.filter(is_active=True)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)


# ==============================
# API Endpoints
# ==============================
@api_view(["POST"])
def register_customer(request):
    """Register a new customer"""
    data = request.data
    try:
        monthly_income = float(data.get("monthly_salary") or data.get("monthly_income", 0))
        approved_limit = round(36 * monthly_income / 100000) * 100000

        customer = Customer.objects.create(
            customer_id=int(data.get("customer_id")),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            age=int(data.get("age")),
            phone_number=data.get("phone_number"),
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            current_debt=0
        )
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def check_eligibility(request):
    """Check loan eligibility"""
    data = request.data
    try:
        customer = Customer.objects.get(customer_id=int(data.get("customer_id")))
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    loan_amount = float(data.get("loan_amount"))
    interest_rate = float(data.get("interest_rate"))
    tenure = int(data.get("tenure"))

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


@api_view(["POST"])
def create_loan(request):
    """Create a loan if eligible"""
    data = request.data
    try:
        customer = Customer.objects.get(customer_id=int(data.get("customer_id")))
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    loan_amount = float(data.get("loan_amount"))
    interest_rate = float(data.get("interest_rate"))
    tenure = int(data.get("tenure"))

    approved, corrected_rate, monthly_installment = check_eligibility_logic(
        customer, loan_amount, interest_rate, tenure
    )

    if not approved:
        return Response({
            "loan_id": None,
            "customer_id": customer.customer_id,
            "loan_approved": False,
            "message": "Loan not approved due to credit score",
            "monthly_installment": round(monthly_installment, 2)
        }, status=status.HTTP_400_BAD_REQUEST)

    last_loan = Loan.objects.order_by("-loan_id").first()
    loan_id = (last_loan.loan_id + 1) if last_loan else 1

    loan = Loan.objects.create(
        loan_id=loan_id,
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_rate,
        monthly_repayment=round(monthly_installment, 2),
        emis_paid_on_time=0,
        is_active=True,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30*tenure)
    )

    return Response({
        "loan_id": loan.loan_id,
        "customer_id": customer.customer_id,
        "loan_approved": True,
        "message": "Loan approved",
        "monthly_installment": round(monthly_installment, 2)
    })


@api_view(["GET"])
def view_loan(request, loan_id):
    """View a single loan"""
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=404)

    return Response({
        "loan_id": loan.loan_id,
        "customer": {
            "customer_id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "age": loan.customer.age,
            "phone_number": loan.customer.phone_number
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "tenure": loan.tenure
    })


@api_view(["GET"])
def view_loans_by_customer(request, customer_id):
    """View all loans of a customer"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    loans = customer.loans.all()
    result = []
    for l in loans:
        repayments_left = max(0, l.tenure - l.emis_paid_on_time)
        result.append({
            "loan_id": l.loan_id,
            "loan_amount": l.loan_amount,
            "interest_rate": l.interest_rate,
            "monthly_installment": l.monthly_repayment,
            "repayments_left": repayments_left
        })

    return Response(result)