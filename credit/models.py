from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max


class Customer(models.Model):
    """
    Internal primary key: id (auto by Django)
    Business ID: customer_id (auto-generated sequential)
    """

    customer_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        editable=False
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True
    )

    monthly_salary = models.PositiveIntegerField(
        help_text="Monthly income of customer"
    )

    approved_limit = models.PositiveIntegerField(
        help_text="Approved credit limit based on salary"
    )

    current_debt = models.PositiveIntegerField(
        default=0,
        help_text="Total outstanding loan amount"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["customer_id"]),
            models.Index(fields=["phone_number"]),
        ]
        ordering = ["customer_id"]

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_id = Customer.objects.aggregate(
                max_id=Max("customer_id")
            )["max_id"]

            self.customer_id = 1 if last_id is None else last_id + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"


class Loan(models.Model):
    """
    Internal primary key: id (auto by Django)
    Business ID: loan_id (auto-generated sequential)
    """

    loan_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        editable=False
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    loan_amount = models.PositiveIntegerField(
        help_text="Principal loan amount"
    )

    tenure = models.PositiveIntegerField(
        help_text="Loan tenure in months"
    )

    interest_rate = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Annual interest rate (percentage)"
    )

    monthly_repayment = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Monthly EMI"
    )

    emis_paid_on_time = models.PositiveIntegerField(
        default=0,
        help_text="Number of EMIs paid on time"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(
        default=True,
        help_text="True if loan is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["loan_id"]),
            models.Index(fields=["customer", "is_active"]),
        ]
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        if not self.loan_id:
            last_id = Loan.objects.aggregate(
                max_id=Max("loan_id")
            )["max_id"]

            self.loan_id = 1 if last_id is None else last_id + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan_id} | Customer {self.customer.customer_id}"