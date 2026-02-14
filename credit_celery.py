import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import django

# ========================
# Set default Django settings
# ========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

# ========================
# Create Celery app
# ========================
app = Celery("credit_system")

# Using Django settings for configuration
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# ========================
# Celery database backend
# ========================
# Store results in Django DB
app.conf.result_backend = "django-db"

# Optional: schedule periodic tasks
app.conf.beat_schedule = {
    # Example: load initial Excel data daily at midnight
    "ingest_customer_loan_data": {
        "task": "credit_celery.ingest_excel_data",
        "schedule": crontab(hour=0, minute=0),
    },
}

# ========================
# Example tasks
# ========================
@app.task
def ingest_excel_data():
    """
    Load data from static/customer_data.xlsx and static/loan_data.xlsx
    into database. Run once for initialization or periodically.
    """
    import pandas as pd
    from credit.models import Customer, Loan
    from datetime import datetime

    # ------------------
    # Customer data
    # ------------------
    try:
        customer_file = os.path.join(settings.BASE_DIR, "static", "customer_data.xlsx")
        df_cust = pd.read_excel(customer_file)
        for _, row in df_cust.iterrows():
            Customer.objects.update_or_create(
                customer_id=int(row["customer_id"]),
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "age": int(row.get("age", 30)),
                    "phone_number": str(row["phone_number"]),
                    "monthly_salary": float(row["monthly_salary"]),
                    "approved_limit": float(row["approved_limit"]),
                    "current_debt": float(row.get("current_debt", 0)),
                }
            )
        print("Customer data ingested successfully.")
    except Exception as e:
        print(f"Error ingesting customer data: {e}")

    # ------------------
    # Loan data
    # ------------------
    try:
        loan_file = os.path.join(settings.BASE_DIR, "static", "loan_data.xlsx")
        df_loan = pd.read_excel(loan_file)
        for _, row in df_loan.iterrows():
            customer = Customer.objects.get(customer_id=int(row["customer_id"]))
            Loan.objects.update_or_create(
                loan_id=int(row["loan_id"]),
                defaults={
                    "customer": customer,
                    "loan_amount": float(row["loan_amount"]),
                    "tenure": int(row["tenure"]),
                    "interest_rate": float(row["interest_rate"]),
                    "monthly_repayment": float(row["monthly_repayment"]),
                    "emis_paid_on_time": int(row.get("EMIs_paid_on_time", 0)),
                    "start_date": pd.to_datetime(row["start_date"]).date() if pd.notna(row["start_date"]) else None,
                    "end_date": pd.to_datetime(row["end_date"]).date() if pd.notna(row["end_date"]) else None,
                    "is_active": True if row.get("is_active", 1) else False,
                }
            )
        print("Loan data ingested successfully.")
    except Exception as e:
        print(f"Error ingesting loan data: {e}")