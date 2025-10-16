from rest_framework.response import Response
from rest_framework import status
from ..models.customer import Customer
from ..serializers.customer import CustomerSerializer
import uuid
from django.db import IntegrityError, connection

def get_customer_list():
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return serializer

def get_customer_by_id(id: int):
    customer = Customer.objects.get(pk=id)
    

def initialize_customer(
    first_name: str,
    last_name: str,
    phone_number: int,
    monthly_salary: int,
    age: int,
):

    approved_limit = monthly_salary * 36
    approved_limit = round(approved_limit / 1_00_000) * 1_00_000
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "age": age,
        "monthly_salary": monthly_salary,
        "approved_limit": approved_limit,
        "current_debt": 0,
    }
    serializer = CustomerSerializer(data=payload)
    if serializer.is_valid():
        try:
            serializer.save()

            # I explicityly added a QUERY for updating id to new one, 
            # but we can add a Counter table that keeps track of "ids" 
            # so we can geenrate new ones
        except IntegrityError:
            try:
                with connection.cursor() as cur:
                    cur.execute(
                        'SELECT setval(pg_get_serial_sequence(\'"Customer"\', \'customer_id\'), COALESCE(MAX(customer_id), 1), true) FROM "Customer";'
                    )
            except Exception:
                pass
            serializer.save()
    return serializer

