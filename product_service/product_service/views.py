from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

products = [{"id": 1, "name": "Achille", "price": 22},{"id": 2, "name": "Matt", "price": 2}]

@api_view(["GET"])
def product_list(request):
    return Response(products)

@api_view(["POST"])
def create_product(request):
    product_data = request.data
    new_product = {
        "id": len(products) + 1,
        "name": product_data.get("name"),
        "price": product_data.get("price"),
    }
    products.append(new_product)
    return Response(new_product, status=status.HTTP_201_CREATED)

@api_view(["GET"])
def get_product(request, productId):
    product = next((p for p in products if p["id"] == productId), None)
    if product is not None:
        return Response(product)
    else:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
