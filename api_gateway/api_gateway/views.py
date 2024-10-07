import requests
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import jwt
from functools import wraps
from jwt.exceptions import PyJWTError


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


class ForwardView(View):
    @token_required
    @role_required(['admin'])
    def post(self, request, service):
        return self._forward_request(request, service, "post")

    @token_required
    @role_required(['user', 'admin'])
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
                response = requests.post(url, json=request.body, headers=headers)
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
