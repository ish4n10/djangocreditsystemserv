from rest_framework import serializers
from ..models.loan import Loan

class LoanSerializer(serializers.ModelSerializer):
    """Simple User serializer"""
    class Meta:
        model = Loan
        fields = ['customer_id', 'loan_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'emis_paid_on_time', 'start_date', 'end_date']
        read_only_fields = ['customer_id', 'loan_id']

