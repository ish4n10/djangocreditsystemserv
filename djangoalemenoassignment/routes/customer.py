from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from ..models.customer import Customer
from ..serializers.customer import CustomerSerializer
from ..helpers.customer_helpers import *

@api_view(['GET', 'POST'])
def customer(request):
    try:
        if request.method == 'GET':
            serializer = get_customer_list()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if request.method == "POST":
            payload = dict(request.data)
            payload.pop('customer_id', None)
            serializer = initialize_customer(**payload)
            if (serializer.is_valid()):
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# def customer_detail(request, pk):

#     try:
#         customer = Customer.objects.get(pk=pk)
#     except Customer.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = CustomerSerializer(customer)
#         return Response(serializer.data, status=status.HTTP_200_OK)

