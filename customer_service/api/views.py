from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

CUSTOMERS = [{"id": 1, "name": "Customer 1"}, {"id": 2, "name": "Customer 2"}]

@api_view(['GET'])
def list_customers(request):
    return Response(CUSTOMERS)

@api_view(['POST'])
def add_customer(request):
    data = request.data

    if 'name' not in data:
        return Response({"error": "Customer name is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    new_customer = {
        "id": len(CUSTOMERS) + 1,
        "name": data['name']
    }
    CUSTOMERS.append(new_customer)
    return Response(new_customer, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_customer(request, customer_id):
    customer = next((c for c in CUSTOMERS if c['id'] == int(customer_id)), None)
    
    if not customer:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(customer)

@api_view(['PUT'])
def update_customer(request, customer_id):
    data = request.data
    customer = next((c for c in CUSTOMERS if c['id'] == int(customer_id)), None)
    
    if not customer:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if 'name' in data:
        customer['name'] = data['name']
    
    return Response(customer)

@api_view(['DELETE'])
def delete_customer(request, customer_id):
    global CUSTOMERS
    customer = next((c for c in CUSTOMERS if c['id'] == int(customer_id)), None)
    
    if not customer:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    CUSTOMERS = [c for c in CUSTOMERS if c['id'] != int(customer_id)]
    return Response({"message": "Customer deleted"}, status=status.HTTP_204_NO_CONTENT)
