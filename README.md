# Credit Approval System 
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="55" style="margin: 0 20px;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg" width="55" style="margin: 0 20px;"/>
  <img src="https://www.django-rest-framework.org/img/logo.png" width="55" style="margin: 0 20px;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="55" style="margin: 0 20px;"/>
  <img src="https://raw.githubusercontent.com/celery/celery/master/docs/images/celery_512.png" width="55" style="margin: 0 20px;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg" width="55" style="margin: 0 20px;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="55" style="margin: 0 20px;"/>
</p>
A production-style backend system that simulates real-world banking credit approval workflows using rule-based risk evaluation and financial scoring logic.

This project implements a complete credit scoring and loan management engine built using Django REST Framework, PostgreSQL, Celery, and Redis. It evaluates loan eligibility based on historical repayment behavior, income constraints, and dynamic risk-adjusted interest rules.

---
<img width="1470" height="753" alt="Screenshot 2026-02-24 at 14 17 08" src="https://github.com/user-attachments/assets/18eb4ed6-5628-4fdf-9cdf-60ac11f49903" />

<img width="1468" height="617" alt="Screenshot 2026-02-24 at 14 17 32" src="https://github.com/user-attachments/assets/40d4f289-afef-41d3-8dbb-2f1a0d83798e" />

<img width="1470" height="663" alt="Screenshot 2026-02-24 at 14 17 54" src="https://github.com/user-attachments/assets/a87e4314-3918-4c59-83de-2d9bb4a85bfa" />

<img width="1470" height="553" alt="Screenshot 2026-02-24 at 14 18 10" src="https://github.com/user-attachments/assets/4fb56c3b-416a-4371-b585-339e17a028b4" />

<img width="1470" height="570" alt="Screenshot 2026-02-24 at 14 18 23" src="https://github.com/user-attachments/assets/83d78401-c8bb-4981-ae65-4c4e0839c6dc" />


## Project Overview

The system is designed to:

- Register customers with dynamically calculated credit limits
- Evaluate loan eligibility using a custom credit scoring engine
- Apply risk-based interest rate correction
- Calculate EMIs using compound interest
- Create and manage full loan lifecycles
- Ingest historical financial data asynchronously
- Expose all functionality through REST APIs

The focus of this project is backend architecture, financial domain modeling, and scalable business logic implementation.

---

## Core Business Logic

### 1️⃣ Credit Limit Calculation

When a customer registers:

approved_limit = 36 × monthly_salary

The value is rounded to the nearest lakh to simulate real-world lending thresholds.

---

### 2️⃣ Credit Score Engine (0–100)

Each loan request triggers a scoring mechanism based on:

- Past loans paid on time
- Total number of loans taken
- Loan activity in the current year
- Total approved loan exposure
- Current active loan volume
- EMI-to-income ratio

Rules enforced:

- If total active loans exceed approved limit → credit score = 0
- If total EMIs exceed 50% of monthly salary → automatic rejection

The system dynamically computes a credit score between 0 and 100 and determines eligibility accordingly.

---

## Risk-Based Loan Approval Logic

| Credit Score | Decision |
|--------------|----------|
| > 50         | Approve loan |
| 30–50        | Approve with interest ≥ 12% |
| 10–30        | Approve with interest ≥ 16% |
| < 10         | Reject loan |

If the requested interest rate does not meet the required risk slab, the system automatically corrects it and returns a `corrected_interest_rate` in the response.

---

### 3️⃣ EMI Calculation (Compound Interest)

The system uses the standard compound interest EMI formula:

EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:

- P = Principal (loan amount)
- r = Monthly interest rate
- n = Tenure in months

If interest rate is zero, EMI defaults to principal divided by tenure.

---

### 4️⃣ Loan Lifecycle Management

When a loan is approved:

- Loan record is created
- EMI is calculated and stored
- Customer current debt is updated
- Loan start and end dates are assigned
- Remaining repayments are tracked dynamically

The system also supports:

- Viewing individual loan details
- Viewing all loans for a customer
- Tracking active and completed loans
- Monitoring repayment progress

---

## Asynchronous Data Processing

The system supports ingestion of historical customer and loan datasets using Celery background workers.

This ensures:

- Non-blocking initialization
- Clean separation of ingestion logic
- Scalable asynchronous task handling
- Production-style architecture

Redis is used as the message broker for background processing.

---

## Architectural Highlights

- Clean separation of concerns (models, services, APIs)
- Modular Django application structure
- Service-layer based credit scoring logic
- RESTful API design with proper validation
- Financial rule engine for risk-based approval
- Dockerized multi-container setup
- PostgreSQL for relational data modeling
- Celery + Redis for asynchronous processing

---

## Technology Stack

- Python  
- Django 4+  
- Django REST Framework  
- PostgreSQL  
- Celery  
- Redis  
- Docker & Docker Compose  

---

## Purpose of the Project

This project was built to simulate a real-world lending backend system and demonstrate:

- Backend system design
- Financial business logic implementation
- Risk evaluation algorithms
- Relational database modeling
- Asynchronous task processing
- Clean and scalable API architecture

It reflects practical backend engineering skills applicable to fintech and high-scale API systems.

---
## Demo Data

The repository includes sample customer and loan datasets under the `/static` directory.
[customer_data.xlsx](https://github.com/user-attachments/files/25515427/customer_data.xlsx)
and
[loan_data.xlsx](https://github.com/user-attachments/files/25515428/loan_data.xlsx)

They are used to demonstrate how the credit scoring engine behaves under different financial conditions.

---

## License

This project is released under the MIT License.

You are free to use, modify, and distribute this software with proper attribution.  
See the LICENSE file for full details.
