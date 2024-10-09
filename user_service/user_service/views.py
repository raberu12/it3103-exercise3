from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

users = [
    {"id": 1, "username": "Achille", "email": "achille@gmail.com", "password": "achille", "role": "user"},
    {"id": 2, "username": "Carlo", "email": "carlo@gmail.com", "password": "carloboy", "role": "user"},
    {"id": 3, "username": "Julz", "email": "julz@gmail.com", "password": "julzstephen", "role": "admin"},
    {"id": 4, "username": "Matt", "email": "matt@gmail.com", "password": "matt0987654321", "role": "admin"},
]

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
            "email": user_data.get("email"),
            "password": user_data.get("password"),
            'role': user_data.get('role', 'user')
        }
        if any(value is None for value in new_user.values()):
            return Response({"error": "Username, email, and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
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
        user["email"] = user_data.get("email", user["email"])
        user["password"] = user_data.get("password", user["password"])
        user["role"] = user_data.get("role", user["role"])
        if any(value is None for value in user.values()):
            return Response({"error": "Username, email, and password must have values."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({k: v for k, v in user.items() if k != 'password'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        user = next((c for c in users if c["id"] == userId), None)
        if user is None:
            return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)
        user_name = user["username"]
        users.remove(user)
        return Response({"message": f"user {user_name} successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
