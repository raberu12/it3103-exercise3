from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

customers = [{"id": 1, "username": "Achille", "email":"achille@gmail.com","password":"achille"}]

@api_view(["GET", "POST", "PUT", "DELETE"])
def customer_view(request, customerId=None):
    if request.method == "GET":
        if customerId is not None:
            customer = next((p for p in customers if p["id"] == customerId), None)
            if customer is not None:
                return Response(customer)
            else:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(customers)

    elif request.method == "POST":
        customer_data = request.data
        new_customer = {
            "id": len(customers) + 1,
            "username": customer_data.get("username"),
            "email": customer_data.get("email"),
            "password":customer_data.get("password")
        }
        if any(value is None for value in new_customer.values()):
            return Response({"error": "Both 'name' and 'price' must have a value."}, status=status.HTTP_400_BAD_REQUEST)
        customers.append(new_customer)
        return Response(new_customer, status=status.HTTP_201_CREATED)

    elif request.method == "PUT":
        if customerId is None:
            return Response({"error": "Customer ID must be provided for updates."}, status=status.HTTP_400_BAD_REQUEST)
        customer = next((p for p in customers if p["id"] == customerId), None)
        if customer is None:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        customer_data = request.data
        customer["username"] = customer_data["username"]
        customer["email"] = customer_data["email"]
        customer["password"] = customer_data["password"]
        if any(value is None for value in customer.values()):
            return Response({"error": "Username,Email, or password price must have a value."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(customer, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        customer = next((p for p in customers if p["id"] == customerId), None)
        if customer is None:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        customerName=customer["username"]
        customers.remove(customer)
        return Response({"message": f"Customer {customerName} successfully deleted."},status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
