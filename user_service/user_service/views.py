from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

users = [
    {"id": 1, "username": "Achille", "password": "achille", "role": "user"},
    {"id": 2, "username": "Carlo", "password": "carloboy", "role": "user"},
    {"id": 3, "username": "Julz", "password": "julzstephen", "role": "admin"},
    {"id": 4, "username": "Matt", "password": "matt0987654321", "role": "admin"},
]

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            for user in users:
                if user['username'] == username and user['password'] == password:
                    return JsonResponse({"id": user['id'],
                                        "username": user['username'],
                                        "role": user['role']}, status=200)
            return JsonResponse({"error": "Invalid credentials"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")  # Default role is 'user'

            # Check if the username already exists
            if any(user["username"] == username for user in users):
                return JsonResponse({"error": "Username already exists."}, status=400)

            # Create a new user
            new_user = {
                "id": len(users) + 1,
                "username": username,
                "password": password,
                'role': role,
            }

            users.append(new_user)  # Add the new user to the list

            return JsonResponse({k: v for k, v in new_user.items() if k != 'password'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@api_view(["GET", "POST", "PUT", "DELETE"])
def user_view(request, userId=None):
    if request.method == "GET":
        if userId is not None:
            user = next((c for c in users if c["id"] == userId), None)
            if user is not None:
                return Response({k: v for k, v in user.items() if k != 'password'})
            else:
                return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(users)

    elif request.method == "POST":
        user_data = request.data
        new_user = {
            "id": len(users) + 1,
            "username": user_data.get("username"),
            "password": user_data.get("password"),
            'role': user_data.get('role', 'user')
        }
        if any(value is None for value in new_user.values()):
            return Response({"error": "Username and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
        users.append(new_user)
        return Response({k: v for k, v in new_user.items() if k != 'password'}, status=status.HTTP_201_CREATED)

    elif request.method == "PUT":
        if userId is None:
            return Response({"error": "user ID must be provided for updates."}, status=status.HTTP_400_BAD_REQUEST)
        user = next((c for c in users if c["id"] == userId), None)
        if user is None:
            return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)
        user_data = request.data
        user["username"] = user_data.get("username", user["username"])
        user["password"] = user_data.get("password", user["password"])
        user["role"] = user_data.get("role", user["role"])
        if any(value is None for value in user.values()):
            return Response({"error": "Username and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({k: v for k, v in user.items() if k != 'password'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        user = next((c for c in users if c["id"] == userId), None)
        if user is None:
            return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)
        user_name = user["username"]
        users.remove(user)
        return Response({"message": f"user {user_name} successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
