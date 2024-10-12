import json
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import requests
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import status
from rest_framework.permissions import AllowAny


def throttle(limit=5, period=60):
    def decorator(func):
        @wraps(func)
        def _wrapped_view(self, request, *args, **kwargs):
            user_id = request.user.get("id")
            key = f"throttle_{user_id}"
            requests_made = cache.get(key, 0)

            if requests_made >= limit:
                return JsonResponse({"error": "Too many requests"}, status=429)

            cache.set(key, requests_made + 1, timeout=period)
            return func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator


def decode_access_token(token):
    try:
        # Decode the token
        decoded_token = AccessToken(token)
        print(decoded_token)
        return {
            "username": decoded_token.get("username"),
            "role": decoded_token.get("role"),
            "id": decoded_token.get("id"),
        }
    except Exception as e:
        raise AuthenticationFailed(f"Token is invalid: {str(e)}")


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")  # Default role is 'user'

            # Check if the username already exists by calling the user service
            user_service_url = settings.SERVICE_URLS["register"]
            check_response = requests.get(
                user_service_url, params={"username": username}
            )

            if check_response.status_code == 200:
                return JsonResponse({"error": "Username already exists."}, status=400)

            # Forward registration request to the user service
            registration_response = requests.post(
                user_service_url,
                json={"username": username, "password": password, "role": role},
            )

            # Return response from user service
            return JsonResponse(
                registration_response.json(), status=registration_response.status_code
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": f"Service request failed: {str(e)}"}, status=500
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def create_tokens_for_user(self, user_data):
        refresh = RefreshToken()
        refresh["username"] = user_data["username"]
        refresh["role"] = user_data["role"]
        refresh["id"] = user_data["id"]
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def post(self, request):
        try:
            data = request.data
            username = data.get("username")
            password = data.get("password")

            user_service_url = settings.SERVICE_URLS["login"]
            response = requests.post(
                user_service_url, json={"username": username, "password": password}
            )

            if response.status_code == 200:
                user_data = response.json()

                # Create tokens using the custom method
                tokens = self.create_tokens_for_user(user_data)

                return Response(
                    {
                        "access": tokens["access"],
                        "refresh": tokens["refresh"],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(response.json(), status=response.status_code)

        except KeyError as e:
            return Response(
                {"error": f"Missing key in user data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProductView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def _check_role(self, request, allowed_roles):
        print(request.headers.get("Authorization"))
        token = request.headers.get("Authorization")
        if not token:
            print("User is not authenticated")
            raise AuthenticationFailed("User is not authenticated")
        payload = decode_access_token(token.split(" ")[1])
        if payload["role"] not in allowed_roles:
            print("User is not authorized")
            raise AuthenticationFailed("User is not authorized")

    def post(self, request):
        print("POST request to create product")  # Debug: log the method call
        self._check_role(request, ["admin"])
        product_data = request.data
        print(f"Product data: {product_data}")  # Debug: log the product data being sent
        return self._forward_request(
            method="POST",
            data=product_data,
            url=settings.SERVICE_URLS["product_create"],
        )

    def put(self, request, productId):
        print(
            f"PUT request to update product with ID {productId}"
        )  # Debug: log the method call
        self._check_role(request, ["admin"])
        return self._forward_request(
            method="PUT",
            data=request.data,
            url=f"{settings.SERVICE_URLS['product_update']}/{productId}/",
        )

    def delete(self, request, productId):
        print(
            f"DELETE request to delete product with ID {productId}"
        )  # Debug: log the method call
        self._check_role(request, ["admin"])
        return self._forward_request(
            method="DELETE",
            data=request.data,
            url=f"{settings.SERVICE_URLS['product_delete']}/{productId}/",
        )

    def get(self, request, productId):
        print(
            f"GET request for product with ID {productId}"
        )  # Debug: log the method call
        return self._forward_request(
            method="GET",
            data=request.data,
            url=f"{settings.SERVICE_URLS['product_get']}/{productId}/",
        )


    def _forward_request(self, method, data, url, headers=None):
        try:
            print(
                f"Forwarding {method} request to {url} with data: {data}"
            )  # Debug: log forwarding details
            response = requests.request(method, url, json=data, headers=headers)

            # Check if response contains JSON content
            if response.headers.get("Content-Type") == "application/json":
                response_data = response.json()
                print(
                    f"Response from service: {response_data}"
                )  # Debug: log the response from service
                return Response(response_data, status=response.status_code)
            else:
                print(
                    f"Non-JSON response from service: {response.text}"
                )  # Log non-JSON response
                return Response(response.text, status=response.status_code)

        except requests.exceptions.RequestException as e:
            print(f"Error in forwarding request: {str(e)}")  # Debug: log the exception
            return Response({"error": f"Service request failed: {str(e)}"}, status=500)
        except ValueError:
            # Handle the case where .json() fails due to invalid JSON
            print(f"Error: Invalid JSON in response. Raw response: {response.text}")
            return Response({"error": "Invalid JSON in response"}, status=500)
