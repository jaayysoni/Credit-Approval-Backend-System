from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Customer(models.Model):
    """
    Customer master table.
    Internal primary key: id (auto by Django)
    External/business ID: customer_id (from Excel & APIs)
    """

    customer_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        help_text="External customer ID from Excel / APIs"
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

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"


class Loan(models.Model):
    """
    Loan table.
    Internal primary key: id (auto by Django)
    External/business ID: loan_id (from Excel & APIs)
    """

    loan_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        help_text="External loan ID from Excel / APIs"
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

    def __str__(self):
        return f"Loan {self.loan_id} | Customer {self.customer.customer_id}"