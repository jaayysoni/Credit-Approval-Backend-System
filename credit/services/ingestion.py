import pandas as pd
from pathlib import Path
from django.db import transaction

from credit.models import Customer, Loan


# Resolve project root safely
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "static"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize Excel column names:
    - strip spaces
    - lowercase
    - replace spaces with underscores
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


@transaction.atomic
def ingest_customers():
    """
    Ingest customers from static/customer_data.xlsx
    Safe & idempotent.
    """

    file_path = STATIC_DIR / "customer_data.xlsx"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    df = pd.read_excel(file_path)
    df = normalize_columns(df)

    print("Customer Excel columns:", list(df.columns))

    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=int(row["customer_id"]),
            defaults={
                "first_name": str(row["first_name"]).strip(),
                "last_name": str(row["last_name"]).strip(),
                "phone_number": str(row["phone_number"]).strip(),
                "monthly_salary": int(row["monthly_salary"]),
                "approved_limit": int(row["approved_limit"]),

                # Not provided → derive later from loans
                "current_debt": 0,

                # Present in Excel
                "age": int(row["age"]),
            },
        )


@transaction.atomic
def ingest_loans():
    """
    Ingest loans from static/loan_data.xlsx
    """

    file_path = STATIC_DIR / "loan_data.xlsx"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    df = pd.read_excel(file_path)
    df = normalize_columns(df)

    print("Loan Excel columns:", list(df.columns))

    for _, row in df.iterrows():
        try:
            customer = Customer.objects.get(
                customer_id=int(row["customer_id"])
            )
        except Customer.DoesNotExist:
            continue

        Loan.objects.update_or_create(
            loan_id=int(row["loan_id"]),
            defaults={
                "customer": customer,
                "loan_amount": float(row["loan_amount"]),
                "tenure": int(row["tenure"]),
                "interest_rate": float(row["interest_rate"]),
                "monthly_repayment": float(row["monthly_payment"]),
                "emis_paid_on_time": int(row["emis_paid_on_time"]),
                "start_date": row["date_of_approval"],
                "end_date": row["end_date"],
                "is_active": True,
            },
        )


def ingest_all():
    """
    Entry point: customers first, then loans.
    """
    ingest_customers()
    ingest_loans()