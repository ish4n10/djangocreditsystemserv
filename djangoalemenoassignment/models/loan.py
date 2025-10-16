from django.db import models

class Loan(models.Model):
    customer_id = models.BigIntegerField()
    loan_id = models.AutoField(primary_key=True) 
    loan_amount = models.BigIntegerField()
    tenure = models.BigIntegerField() # in months
    interest_rate = models.FloatField()
    monthly_repayment = models.BigIntegerField()
    emis_paid_on_time = models.BigIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta: 
        db_table = 'Loan'
