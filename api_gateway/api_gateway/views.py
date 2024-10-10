import json
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from jwt.exceptions import PyJWTError
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

def token_required(f):
    @wraps(f)
    def decorated(self, request, *args, **kwargs):
        token = request.headers.get("Authorization")
        print(f"Received Token: {token}")  # Log received token

        if not token:
            return JsonResponse({"error": "Token is missing"}, status=401)

        try:
            scheme, _, jwt_token = token.partition(' ')
            if scheme.lower() != 'bearer':
                return JsonResponse({"error": "Authorization header must start with Bearer"}, status=401)

            # Decode the JWT
            data = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = data  # Attach user data to request
            print(f"Decoded User Data: {data}")  # Log decoded user data

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

        return f(self, request, *args, **kwargs)

    return decorated

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(self, request, *args, **kwargs):
            user_role = request.user.get("role") if hasattr(request, 'user') else None
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

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")  # Default role is 'user'

            # Check if the username already exists by calling the user service
            user_service_url = settings.SERVICE_URLS['register']
            check_response = requests.get(user_service_url, params={"username": username})

            if check_response.status_code == 200:
                return JsonResponse({"error": "Username already exists."}, status=400)

            # Forward registration request to the user service
            registration_response = requests.post(user_service_url, json={
                "username": username,
                "password": password,
                "role": role
            })

            # Return response from user service
            return JsonResponse(registration_response.json(), status=registration_response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Service request failed: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user_service_url = settings.SERVICE_URLS['login']
            response = requests.post(user_service_url,json={"username": username, "password": password})

            if response.status_code == 200:
                user_data = response.json()
                payload = {
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'role': user_data['role'],
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

                return JsonResponse({"token": token}, status=200)
            else:
                return JsonResponse(response.json(), status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
    @token_required
    @role_required(["admin"])
    def post(self, request):
        product_data = request.data  # This works with DRF
        return self._forward_request(request, product_data, settings.SERVICE_URLS['product_create'])

    @token_required
    @role_required(["admin"])
    def put(self, request, productId):
        return self._forward_request(request, request.data, f"{settings.SERVICE_URLS['product_update']}/{productId}/")

    @token_required
    @role_required(["admin"])
    def delete(self, request, productId):
        return self._forward_request(request, request.data, f"{settings.SERVICE_URLS['product_delete']}/{productId}/")

    @token_required
    @role_required(["admin", "user"])
    def get(self, request, productId):
        return self._forward_request(request, request.data, f"{settings.SERVICE_URLS['product_get']}/{productId}/")

    def _forward_request(self, request, product_data, url):
        headers = {"Authorization": request.headers.get("Authorization")}
        try:
            response = requests.post(url, json=product_data, headers=headers)
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Service request failed: {str(e)}"}, status=500)
