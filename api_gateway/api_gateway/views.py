import json
from datetime import datetime, timedelta

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

import requests



def token_required(f):
    @wraps(f)
    def decorated(self, request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return JsonResponse({"error": "Token is missing"}, status=401)
        try:
            data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except PyJWTError as e:
            return JsonResponse({"error": f"Token is invalid: {str(e)}"}, status=401)
        except Exception as e:
            return JsonResponse(
                {"error": f"An unexpected error occurred: {str(e)}"}, status=500
            )
        return f(self, request, *args, **kwargs)

    return decorated


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(self, request, *args, **kwargs):
            if not hasattr(request, "user"):
                return JsonResponse({"error": "User not authenticated"}, status=401)

            user_role = request.user.get("role")
            if not user_role or user_role not in allowed_roles:
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

class ForwardView(View):
    @token_required
    @role_required(["admin"])
    def post(self, request, service):
        return self._forward_request(request, service, "post")

    @token_required
    @role_required(["user", "admin"])
    @throttle(limit=5, period=60)
    def get(self, request, service):
        return self._forward_request(request, service, "get")

    def _forward_request(self, request, service, method):
        service_urls = settings.SERVICE_URLS
        url = service_urls.get(service)
        if not url:
            return JsonResponse({"error": "Service not found"}, status=404)

        headers = {"Authorization": request.headers.get("Authorization")}
        try:
            if method == "post":
                response = requests.post(
                    url, json=json.loads(request.body), headers=headers
                )
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"error": f"Service request failed: {str(e)}"}, status=500
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid JSON response from service: {str(e)}"}, status=500
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"An unexpected error occurred: {str(e)}"}, status=500
            )
