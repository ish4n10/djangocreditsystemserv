from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from djangoalemenoassignment.serializers.loan import LoanSerializer
from ..helpers.loan_helpers import check_loan_eligibility
from ..models.loan import Loan
from ..models.customer import Customer
from ..background_workers.loan_ingest_worker import worker as loan_ingest_worker
from ..background_workers.customer_ingest_worker import worker as customer_ingest_worker
from django.db import IntegrityError, connection
import math

@api_view(['POST'])
def check_loan_eligibility_view(request):
  
    try:
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return Response(
                {'error': 'Missing required fields: customer_id, loan_amount, interest_rate, tenure'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eligibility_result = check_loan_eligibility(
            customer_id=customer_id,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure
        )

        
        monthly_installment = 0
         
        if eligibility_result['approval_status'] == 'approved':
             final_rate = eligibility_result.get('corrected_interest_rate', interest_rate)
             total_interest = (loan_amount * final_rate * tenure) / 100
             monthly_installment = (loan_amount + total_interest) / tenure
        
        response_data = {
            'customer_id': customer_id,
            'approval': eligibility_result['approval_status'] == 'approved',
            'interest_rate': interest_rate,
            'corrected_interest_rate': eligibility_result.get('corrected_interest_rate'),
            'tenure': tenure,
            'monthly_installment': round(monthly_installment, 2) if monthly_installment > 0 else 0
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_loan_view(request):
    try:
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return Response(
                {'error': 'Missing required fields: customer_id, loan_amount, interest_rate, tenure'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Do not accept client-provided loan_id; PK is auto
        _ = request.data.get('loan_id', None)

        customer_id = int(customer_id)
        loan_amount = float(loan_amount)
        interest_rate = float(interest_rate)
        tenure = int(tenure)

        serializer = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)
        loan_approved = serializer.get('approval_status') == 'approved'

        message = None
        loan_id = None
        monthly_installment = 0.0

        if loan_approved:
            final_rate = serializer.get('corrected_interest_rate', interest_rate)
            total_interest = (loan_amount * final_rate * tenure) / 100
            monthly_installment = round((loan_amount + total_interest) / tenure, 2)


            from django.utils import timezone
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=30 * tenure)

            try:
                loan = Loan.objects.create(
                    customer_id=customer_id,
                    loan_amount=int(loan_amount),
                    tenure=tenure,
                    interest_rate=int(final_rate),
                    monthly_repayment=int(monthly_installment),
                    emis_paid_on_time=0,
                    start_date=start_date,
                    end_date=end_date,
                )
            except IntegrityError:
                # Sequence may be out of sync; reseed and retry once
                try:
                    with connection.cursor() as cur:
                        cur.execute(
                            'SELECT setval(pg_get_serial_sequence(\'"Loan"\', \'loan_id\'), COALESCE(MAX(loan_id), 1), true) FROM "Loan";'
                        )
                except Exception:
                    pass
                loan = Loan.objects.create(
                    customer_id=customer_id,
                    loan_amount=int(loan_amount),
                    tenure=tenure,
                    interest_rate=int(final_rate),
                    monthly_repayment=int(monthly_installment),
                    emis_paid_on_time=0,
                    start_date=start_date,
                    end_date=end_date,
                )
            loan_id = loan.loan_id
        else:
            message = 'Loan not approved'

        response = {
            'loan_id': loan_id,
            'customer_id': customer_id,
            'loan_approved': loan_approved,
            'message': message,
            'monthly_installment': monthly_installment,
        }

        return Response(response, status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_loan_by_id_view(request, loan_id: int):
    try:
        loan = Loan.objects.get(pk=loan_id)
        customer = Customer.objects.get(customer_id=loan.customer_id)

        response_data = {
            'loan_id': loan.loan_id,
            'customer': {
                'id': customer.customer_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number,
                'age': customer.age,
            },
            'loan_amount': float(loan.loan_amount),
            'interest_rate': float(loan.interest_rate),
            'monthly_installment': float(loan.monthly_repayment),
            'tenure': int(loan.tenure),
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found for this loan"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_loans_by_customer_id_view(request, customer_id: int):
    try:
        loans = Loan.objects.filter(customer_id=customer_id).order_by('-start_date')
        response_items = []
        for loan in loans:
            repayments_left = max(int(loan.tenure) - int(loan.emis_paid_on_time or 0), 0)
            response_items.append({
                'loan_id': int(loan.loan_id),
                'loan_amount': float(loan.loan_amount),
                'interest_rate': float(loan.interest_rate),
                'monthly_installment': float(loan.monthly_repayment),
                'repayments_left': repayments_left,
            })
        return Response(response_items, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
