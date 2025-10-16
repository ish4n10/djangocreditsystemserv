from django.db import models
import uuid

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    create_ts = models.DateTimeField(auto_now_add=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    age = models.IntegerField()
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.FloatField()

    class Meta:
        db_table = 'Customer'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
