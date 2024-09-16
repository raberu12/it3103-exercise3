from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests

ORDERS = []  # List to store orders

CUSTOMER_SERVICE_URL = "http://localhost:3001/customers/"
PRODUCT_SERVICE_URL = "http://localhost:3002/products/"

# Helper functions
def verify_customer(customer_id):
    response = requests.get(f"{CUSTOMER_SERVICE_URL}{customer_id}/")
    return response.status_code == 200

def verify_product(product_id):
    response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}/")
    return response.status_code == 200

@api_view(['POST', 'GET', 'PUT', 'DELETE'])
def order_handler(request, order_id=None):
    global ORDERS

    # GET request to list all orders (for root URL or /orders)
    if request.method == 'GET':
        if order_id is None:
            return Response(ORDERS)  # Return the list of all orders
        else:
            # Return specific order details by ID
            order = next((order for order in ORDERS if order['id'] == order_id), None)
            if not order:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(order)

    # POST /orders: Create a new order
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not customer_id or not product_id:
            return Response({"error": "Customer ID and Product ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_customer(customer_id):
            return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if not verify_product(product_id):
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)

        order_id = len(ORDERS) + 1
        new_order = {
            "id": order_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity
        }
        ORDERS.append(new_order)
        return Response(new_order, status=status.HTTP_201_CREATED)

    # PUT /orders/:orderId: Update an order
    if request.method == 'PUT' and order_id is not None:
        order = next((order for order in ORDERS if order['id'] == order_id), None)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        customer_id = request.data.get('customer_id', order['customer_id'])
        product_id = request.data.get('product_id', order['product_id'])
        quantity = request.data.get('quantity', order['quantity'])

        if not verify_customer(customer_id):
            return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if not verify_product(product_id):
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)

        order.update({
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity
        })

        return Response(order)

    # DELETE /orders/:orderId: Delete an order
    if request.method == 'DELETE' and order_id is not None:
        order = next((order for order in ORDERS if order['id'] == order_id), None)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        ORDERS = [order for order in ORDERS if order['id'] != order_id]
        return Response({"message": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
