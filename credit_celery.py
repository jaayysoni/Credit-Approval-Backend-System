import os
import django
import logging
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# ========================
# Set up Django environment
# ========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

# ========================
# Logger
# ========================
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ========================
# Create Celery app
# ========================
app = Celery("credit_system")

# Load Celery config from Django settings using CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# ========================
# Celery Beat schedule
# ========================
app.conf.beat_schedule = {
    "ingest_customer_loan_data": {
        "task": "credit_celery.ingest_excel_data",
        "schedule": crontab(hour=0, minute=0),  # daily at midnight
        "args": (),
    },
}

# ========================
# Celery Task: ingest_excel_data
# ========================
@app.task(bind=True, name="credit_celery.ingest_excel_data")
def ingest_excel_data(self):
    """
    Load customer_data.xlsx and loan_data.xlsx into the database.
    Can be triggered manually or via Celery Beat.
    """
    import pandas as pd
    from credit.models import Customer, Loan

    # ------------------
    # Customer Data
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
                },
            )
        logger.info("✅ Customer data ingested successfully.")

    except FileNotFoundError:
        logger.error("Customer Excel file not found.")
    except Exception as e:
        logger.error(f"Error ingesting customer data: {e}", exc_info=True)

    # ------------------
    # Loan Data
    # ------------------
    try:
        loan_file = os.path.join(settings.BASE_DIR, "static", "loan_data.xlsx")
        df_loan = pd.read_excel(loan_file)

        for _, row in df_loan.iterrows():
            try:
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
                        "start_date": pd.to_datetime(row["start_date"]).date()
                        if pd.notna(row["start_date"])
                        else None,
                        "end_date": pd.to_datetime(row["end_date"]).date()
                        if pd.notna(row["end_date"])
                        else None,
                        "is_active": bool(row.get("is_active", 1)),
                    },
                )
            except Customer.DoesNotExist:
                logger.warning(f"Customer ID {row['customer_id']} not found. Skipping loan {row['loan_id']}.")

        logger.info("✅ Loan data ingested successfully.")

    except FileNotFoundError:
        logger.error("Loan Excel file not found.")
    except Exception as e:
        logger.error(f"Error ingesting loan data: {e}", exc_info=True)