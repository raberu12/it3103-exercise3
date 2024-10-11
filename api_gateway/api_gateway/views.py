import json
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken


def token_required(f):
    @wraps(f)
    def decorated(self, request, *args, **kwargs):
        try:
            auth = TokenAuthentication()
            user, token = auth.authenticate(request)
            request.user = user
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=401)
        return f(self, request, *args, **kwargs)

    return decorated


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(self, request, *args, **kwargs):
            user_role = request.user.get("role") if hasattr(request, "user") else None
            if user_role not in allowed_roles:
                return JsonResponse({"error": "Permission denied"}, status=403)
            return f(self, request, *args, **kwargs)

        return decorated

    return decorator


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
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user_service_url = settings.SERVICE_URLS["login"]
            response = requests.post(
                user_service_url, json={"username": username, "password": password}
            )

            if response.status_code == 200:
                user_data = response.json()

                # Create JWT payload manually (without for_user)
                refresh = RefreshToken()
                refresh["username"] = user_data["username"]
                refresh["role"] = user_data["role"]
                refresh["id"] = user_data["id"]

                return JsonResponse(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": user_data,
                    },
                    status=200,
                )
            else:
                return JsonResponse(response.json(), status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ProductView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _check_role(self, request, allowed_roles):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("User is not authenticated")

        user_role = getattr(request.user, "role", None)
        if user_role not in allowed_roles:
            raise PermissionDenied("Permission denied")

    def post(self, request):
        self._check_role(request, ["admin"])
        product_data = request.data
        return self._forward_request(
            product_data, settings.SERVICE_URLS["product_create"]
        )

    def put(self, request, productId):
        self._check_role(request, ["admin"])
        return self._forward_request(
            request.data,
            f"{settings.SERVICE_URLS['product_update']}/{productId}/",
        )

    def delete(self, request, productId):
        self._check_role(request, ["admin"])
        return self._forward_request(
            request.data,
            f"{settings.SERVICE_URLS['product_delete']}/{productId}/",
        )

    def get(self, request, productId):
        self._check_role(request, ["admin", "user"])
        return self._forward_request(
            request.data,
            f"{settings.SERVICE_URLS['product_get']}/{productId}/",
        )

    def _forward_request(self, product_data, url, headers=None):
        try:
            response = requests.post(url, json=product_data, headers=headers)
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Service request failed: {str(e)}"}, status=500)
