from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests

ORDERS = []

USER_SERVICE_URL = "http://localhost:3002/users/"
PRODUCT_SERVICE_URL = "http://localhost:3001/products/"


def get_user_details(user_id):
    try:
        headers = {
            "Authorization": "Bearer <token_value>"
        } 
        response = requests.get(f"{USER_SERVICE_URL}{user_id}/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def get_product_details(product_id):
    try:
        headers = {'Authorization': 'Bearer <token_value>'} 
        response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


@api_view(["POST", "GET", "PUT", "DELETE"])
def order_handler(request, order_id=None):
    global ORDERS

    def enrich_order(order):
        user_details = get_user_details(order["user_id"])
        product_details = get_product_details(order["product_id"])
        total_price = (
            product_details["price"] * order["quantity"] if product_details else 0
        )

        return {
            "id": order["id"],
            "user_id": order["user_id"],
            "user_name": user_details["username"] if user_details else "Unknown",
            "product_id": order["product_id"],
            "product_name": product_details["name"] if product_details else "Unknown",
            "quantity": order["quantity"],
            "price_per_unit": product_details["price"] if product_details else 0,
            "total_price": total_price,
        }

    if request.method == "GET":
        if order_id is None:
            enriched_orders = [enrich_order(order) for order in ORDERS]
            return Response(enriched_orders)
        else:
            order = next((order for order in ORDERS if order["id"] == order_id), None)
            if not order:
                return Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response(enrich_order(order))

    if request.method == "POST":
        try:
            user_id = request.data.get("user_id")
            product_id = request.data.get("product_id")
            quantity = request.data.get("quantity", 1)

            if not user_id or not product_id:
                return Response(
                    {"error": "user ID and Product ID are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not get_user_details(user_id):
                return Response(
                    {"error": "user does not exist"}, status=status.HTTP_404_NOT_FOUND
                )

            product_details = get_product_details(product_id)
            if not product_details:
                return Response(
                    {"error": "Product does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            order_id = len(ORDERS) + 1
            new_order = {
                "id": order_id,
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
            }
            ORDERS.append(new_order)
            return Response(enrich_order(new_order), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if request.method == "PUT" and order_id is not None:
        try:
            order = next((order for order in ORDERS if order["id"] == order_id), None)
            if not order:
                return Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )

            user_id = request.data.get("user_id", order["user_id"])
            product_id = request.data.get("product_id", order["product_id"])
            quantity = request.data.get("quantity", order["quantity"])

            if not get_user_details(user_id):
                return Response(
                    {"error": "user does not exist"}, status=status.HTTP_404_NOT_FOUND
                )

            if not get_product_details(product_id):
                return Response(
                    {"error": "Product does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            order.update(
                {"user_id": user_id, "product_id": product_id, "quantity": quantity}
            )

            return Response(enrich_order(order))
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if request.method == "DELETE" and order_id is not None:
        try:
            order = next((order for order in ORDERS if order["id"] == order_id), None)
            if not order:
                return Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )

            ORDERS = [order for order in ORDERS if order["id"] != order_id]
            return Response(
                {"message": "Order deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
