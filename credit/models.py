from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()

    phone_number = models.CharField(max_length=15, unique=True)

    monthly_salary = models.PositiveIntegerField()
    approved_limit = models.PositiveIntegerField()
    current_debt = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["customer_id"]

    def __str__(self):
        return f"{self.customer_id} - {self.first_name} {self.last_name}"


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)

    # This creates `customer_id` column in DB (as required)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="loans",
        db_index=True
    )

    loan_amount = models.FloatField()
    tenure = models.PositiveIntegerField(help_text="Tenure in months")
    interest_rate = models.FloatField()

    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.PositiveIntegerField(default=0)

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer_id}"