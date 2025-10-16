from django.urls import path
from .customer import customer
from .loan import check_loan_eligibility_view, create_loan_view, get_loan_by_id_view, get_loans_by_customer_id_view

urlpatterns = [
    path('register/', customer, name='customer'),
    path('check-eligibility/', check_loan_eligibility_view, name='check-loan-eligibility'),
    path('create-loan/', create_loan_view, name='create-loan'),
    path('view-loan/<int:loan_id>/', get_loan_by_id_view, name='get-loan-by-id'),
    path('view-loans/<int:customer_id>/', get_loans_by_customer_id_view, name='get-loans-by-customer-id'),
]
