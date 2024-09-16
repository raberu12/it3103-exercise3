from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

products = [{"id": 1, "name": "Achille", "price": 22},{"id": 2, "name": "Matt", "price": 2}]

@api_view(["GET", "POST", "PUT", "DELETE"])
def product_view(request, productId=None):
    if request.method == "GET":
        if productId is not None:
            product = next((p for p in products if p["id"] == productId), None)
            if product is not None:
                return Response(product)
            else:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(products)

    elif request.method == "POST":
        product_data = request.data
        new_product = {
            "id": len(products) + 1,
            "name": product_data.get("name"),
            "price": product_data.get("price"),
        }
        if any(value is None for value in new_product.values()):
            return Response({"error": "Both 'name' and 'price' must have a value."}, status=status.HTTP_400_BAD_REQUEST)
        products.append(new_product)
        return Response(new_product, status=status.HTTP_201_CREATED)

    elif request.method == "PUT":
        if productId is None:
            return Response({"error": "Product ID must be provided for updates."}, status=status.HTTP_400_BAD_REQUEST)
        product = next((p for p in products if p["id"] == productId), None)
        if product is None:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        product_data = request.data
        product["name"] = product_data["name"]
        product["price"] = product_data["price"]
        if any(value is None for value in product.values()):
            return Response({"error": "Both 'name' and 'price' must have a value."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(product, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        product = next((p for p in products if p["id"] == productId), None)
        if product is None:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        productName=product["name"]
        products.remove(product)
        return Response({"message": f"Product {productName} successfully deleted."},status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
