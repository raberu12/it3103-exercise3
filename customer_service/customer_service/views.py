from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

customers = [
    {"id": 1, "username": "Achille", "email": "achille@gmail.com", "password": "achille"},
    {"id": 2, "username": "Carlo", "email": "carlo@gmail.com", "password": "carloboy"},
    {"id": 3, "username": "Julz", "email": "julz@gmail.com", "password": "julzstephen"},
    {"id": 4, "username": "Matt", "email": "matt@gmail.com", "password": "matt0987654321"},
]

@api_view(["GET", "POST", "PUT", "DELETE"])
def customer_view(request, customerId=None):
    if request.method == "GET":
        if customerId is not None:
            customer = next((c for c in customers if c["id"] == customerId), None)
            if customer is not None:
                return Response({k: v for k, v in customer.items() if k != 'password'})
            else:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(customers)

    elif request.method == "POST":
        customer_data = request.data
        new_customer = {
            "id": len(customers) + 1,
            "username": customer_data.get("username"),
            "email": customer_data.get("email"),
            "password": customer_data.get("password")
        }
        if any(value is None for value in new_customer.values()):
            return Response({"error": "Username, email, and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
        customers.append(new_customer)
        return Response({k: v for k, v in new_customer.items() if k != 'password'}, status=status.HTTP_201_CREATED)

    elif request.method == "PUT":
        if customerId is None:
            return Response({"error": "Customer ID must be provided for updates."}, status=status.HTTP_400_BAD_REQUEST)
        customer = next((c for c in customers if c["id"] == customerId), None)
        if customer is None:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        customer_data = request.data
        customer["username"] = customer_data.get("username", customer["username"])
        customer["email"] = customer_data.get("email", customer["email"])
        customer["password"] = customer_data.get("password", customer["password"])
        if any(value is None for value in customer.values()):
            return Response({"error": "Username, email, and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({k: v for k, v in customer.items() if k != 'password'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        customer = next((c for c in customers if c["id"] == customerId), None)
        if customer is None:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        customer_name = customer["username"]
        customers.remove(customer)
        return Response({"message": f"Customer {customer_name} successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
