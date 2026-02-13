import pandas as pd
from credit.models import Customer, Loan
from celery import shared_task
from django.db import transaction
from datetime import datetime


@shared_task
def ingest_customers(file_path):
    """
    Reads customer_data.xlsx and inserts customers into DB
    """
    df = pd.read_excel(file_path)

    with transaction.atomic():
        for _, row in df.iterrows():
            # Calculate approved_limit as per assignment: 36 * monthly_salary, rounded to nearest lakh
            approved_limit = round(row['monthly_salary'] * 36 / 100000) * 100000

            Customer.objects.update_or_create(
                phone_number=str(row['phone_number']),
                defaults={
                    "first_name": row['first_name'],
                    "last_name": row['last_name'],
                    "age": row.get('age', 30),  # fallback if missing
                    "monthly_salary": row['monthly_salary'],
                    "approved_limit": approved_limit,
                    "current_debt": row.get('current_debt', 0)
                }
            )
    return f"{len(df)} customers ingested"


@shared_task
def ingest_loans(file_path):
    """
    Reads loan_data.xlsx and inserts loans into DB
    """
    df = pd.read_excel(file_path)

    with transaction.atomic():
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['customer_id'])
            except Customer.DoesNotExist:
                continue  # skip if customer not found

            Loan.objects.update_or_create(
                loan_id=row['loan_id'],
                defaults={
                    "customer": customer,
                    "loan_amount": row['loan_amount'],
                    "tenure": row['tenure'],
                    "interest_rate": row['interest_rate'],
                    "monthly_repayment": row['monthly_repayment'],
                    "emis_paid_on_time": row.get('EMIs_paid_on_time', 0),
                    "start_date": pd.to_datetime(row['start_date']).date(),
                    "end_date": pd.to_datetime(row['end_date']).date()
                }
            )
    return f"{len(df)} loans ingested"