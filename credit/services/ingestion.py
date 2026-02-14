import pandas as pd
from credit.models import Customer, Loan

# ========================
# Helper functions
# ========================
def normalize_columns(df):
    """Normalize column names: lowercase + replace spaces with underscores + strip"""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

def safe_date(val):
    """Convert pandas Timestamp/NaT to Python date or None"""
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return val.date()
    return val

# ========================
# Load customer data
# ========================
customer_file = "static/customer_data.xlsx"
df_customers = pd.read_excel(customer_file)
df_customers = normalize_columns(df_customers)

# Add current_debt column if missing
if "current_debt" not in df_customers.columns:
    df_customers["current_debt"] = 0

for _, row in df_customers.iterrows():
    Customer.objects.update_or_create(
        customer_id=row["customer_id"],
        defaults={
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "age": row["age"],
            "phone_number": str(row["phone_number"]),
            "monthly_salary": row["monthly_salary"],
            "approved_limit": row["approved_limit"],
            "current_debt": row["current_debt"],
        }
    )

print(f"Loaded {df_customers.shape[0]} customers")

# ========================
# Load loan data
# ========================
loan_file = "static/loan_data.xlsx"
df_loans = pd.read_excel(loan_file)
df_loans = normalize_columns(df_loans)

# Map known column name differences
column_mapping = {
    "monthly_payment": "monthly_repayment",
    "em_is_paid_on_time": "emis_paid_on_time",
    "date_of_approval": "start_date",
}

df_loans = df_loans.rename(columns={k: v for k, v in column_mapping.items() if k in df_loans.columns})

# Set defaults for missing columns
optional_columns_defaults = {
    "monthly_repayment": 0,
    "emis_paid_on_time": 0,
    "start_date": None,
    "end_date": None,
    "is_active": True,
}

for col, default in optional_columns_defaults.items():
    if col not in df_loans.columns:
        df_loans[col] = default

# Convert date columns safely
for date_col in ["start_date", "end_date"]:
    if date_col in df_loans.columns:
        df_loans[date_col] = df_loans[date_col].apply(safe_date)

for _, row in df_loans.iterrows():
    try:
        customer = Customer.objects.get(customer_id=row["customer_id"])
        Loan.objects.update_or_create(
            loan_id=row["loan_id"],
            defaults={
                "loan_amount": row["loan_amount"],
                "tenure": row["tenure"],
                "interest_rate": row["interest_rate"],
                "monthly_repayment": row["monthly_repayment"],
                "emis_paid_on_time": row["emis_paid_on_time"],
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "is_active": row["is_active"],
                "customer": customer,
            }
        )
    except Customer.DoesNotExist:
        print(f"Customer with ID {row['customer_id']} not found. Skipping loan {row['loan_id']}.")

print(f"Loaded {df_loans.shape[0]} loans")