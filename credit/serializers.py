# credit/serializers.py

from rest_framework import serializers
from .models import Customer, Loan


# ================================
# Customer Serializer
# ================================
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ("customer_id", "created_at")


# ================================
# Loan Serializer (Full Loan View)
# ================================
class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ("loan_id", "created_at")


# ================================
# Check Eligibility Serializer
# (For /check-eligibility endpoint)
# ================================
class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.IntegerField(min_value=1)
    interest_rate = serializers.FloatField(min_value=0.0)
    tenure = serializers.IntegerField(min_value=1)


# ================================
# Create Loan Serializer
# (For /create-loan endpoint)
# ================================
class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.IntegerField(min_value=1)
    interest_rate = serializers.FloatField(min_value=0.0)
    tenure = serializers.IntegerField(min_value=1)