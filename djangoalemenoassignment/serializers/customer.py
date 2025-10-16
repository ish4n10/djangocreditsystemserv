from rest_framework import serializers
from ..models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Simple User serializer"""
    class Meta:
        model = Customer
        fields = ['customer_id', 'create_ts', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
        read_only_fields = ['customer_id', 'create_ts']
