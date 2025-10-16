from ..models.loan import Loan
from ..models.customer import Customer
from ..serializers.loan import LoanSerializer
from datetime import datetime, date
from django.utils import timezone

def get_all_loans():
    loans = Loan.objects.all()
    serializer = LoanSerializer(loans, many=True)
    return serializer

    
def get_loans_by_customer_id(customer_id: int):
    loans = Loan.objects.filter(customer_id=customer_id).order_by('-start_date')
    serializer = LoanSerializer(loans, many=True)
    return serializer

def generate_customer_credit_score(customer_id: int):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        
        loan_list = get_loans_by_customer_id(customer_id=customer_id)
        loan_list = loan_list.data
        
        credit_score = 0
        total_loans = len(loan_list)
        loans_paid_on_time = 0
        current_year_loans = 0
        total_loan_volume = 0
        current_loans_sum = 0
        current_year = datetime.now().year
        
        for loan in loan_list:
            # 1 and 2 
            if loan['emis_paid_on_time'] > 0:
                loans_paid_on_time += 1
            
            # 3
            if isinstance(loan['start_date'], str):
                start_date = datetime.fromisoformat(loan['start_date'].replace('Z', '+00:00'))
            else:
                start_date = loan['start_date']
            
            if start_date.year == current_year:
                current_year_loans += 1
            
            # loan volume
            total_loan_volume += loan['loan_amount']
            
            current_loans_sum += loan['loan_amount']
        
        if current_loans_sum > customer.approved_limit:
            return {
                'credit_score': 0,
                'approval_status': 'rejected'
            }
        
        if total_loans > 0:
            on_time_ratio = loans_paid_on_time / total_loans
            credit_score += int(on_time_ratio * 30) 
        
        if total_loans <= 3:
            credit_score += 25
        elif total_loans <= 6:
            credit_score += 15
        else:
            credit_score += 5
        
        if current_year_loans > 0:
            credit_score += 15
        
        if total_loan_volume > 0:
            volume_score = min(20, int(total_loan_volume / 100000)) 
            credit_score += volume_score
        
        credit_score = min(100, credit_score)
        
        return {
            'credit_score': credit_score,
            'approval_status': 'approved'
        }
        
    except Customer.DoesNotExist:
        return {
            'credit_score': 0,
            'approval_status': 'rejected'
        }
    except Exception as e:
        return {
            'credit_score': 0,
            'approval_status': 'rejected'
        }


def check_loan_eligibility(customer_id: int, loan_amount: int, interest_rate: float, tenure: int):

    try:
       
        customer = Customer.objects.get(customer_id=customer_id)
        
        credit_data = generate_customer_credit_score(customer_id)
        credit_score = credit_data['credit_score']
        
        current_loans_sum = credit_data.get('current_loans_sum', 0)
        if current_loans_sum + loan_amount > customer.approved_limit:
            return {
                'approval_status': 'rejected',
                'corrected_interest_rate': None
            }
        
        current_monthly_emi = 0
        loan_list = get_loans_by_customer_id(customer_id=customer_id)
        for loan in loan_list.data:
            current_monthly_emi += loan['monthly_repayment']
        
        new_loan_emi = (loan_amount * interest_rate / 100) / 12  
        total_emi = current_monthly_emi + new_loan_emi # Got from EMI calculator
        
        if total_emi > (customer.monthly_salary * 0.5):
            return {
                'approval_status': 'rejected',
                'corrected_interest_rate': None
            }
        
        corrected_interest_rate = interest_rate
        
        if credit_score > 50:
            approval_status = 'approved'
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval_status = 'approved'
            else:
                approval_status = 'rejected'
                corrected_interest_rate = 12.01  # lowest of slab
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval_status = 'approved'
            else:
                approval_status = 'rejected'
                corrected_interest_rate = 16.01 
        else:
            approval_status = 'rejected'
            corrected_interest_rate = None
        
        return {
            'approval_status': approval_status,
            'credit_score': credit_score,
            'corrected_interest_rate': corrected_interest_rate
        }
        
    except Customer.DoesNotExist:
        return {
            'approval_status': 'rejected',
            'corrected_interest_rate': None
        }
    except Exception as e:
        return {
            'approval_status': 'rejected',
            'corrected_interest_rate': None
        }
