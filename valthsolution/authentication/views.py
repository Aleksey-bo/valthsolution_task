from datetime import timedelta

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from core.permission import JWTAuth
from .serializer import UserSerializer
from core.jwt_utils import encode_jwt
from core.config import ACCESS_TOKEN_EXPIRE_MINUTS


User = get_user_model()

# Create your views here.
class AuthViewSet(ViewSet):
    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING)
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        enum=["Invalid credentials", "Token expired", "Invalid token"]
                    )
                }
            ),
            500: openapi.Response(description="Internal Server Error")
        }
    )
    @action(detail=False, methods=["post"], url_path="sign_in", url_name="sign_in")
    def sign_in(self, request):
        try:
            data = request.data
            user_instance = authenticate(
                username=data.get("username"),
                password=data.get("password")
            )
            if user_instance is None:
                return Response({'error': 'Invalid credentials'}, status=401)
            
            token = encode_jwt(data={
                "username": user_instance.username
            }, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTS))
            return Response({
                "access_token": token
            }, status=200)
        except AuthenticationFailed as e:
            return Response({"error": e}, status=401)
        except Exception as e:
            print(e)
            return Response({"error": "Internal Server Error"}, status=500)

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING)
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        enum=["Invalid credentials", "Token expired", "Invalid token"]
                    )
                }
            ),
            500: openapi.Response(description="Internal Server Error")
        }
    )
    @action(detail=False, methods=["post"], url_path="sign_up", url_name="sign_up")
    def sign_up(self, request):
        try:
            data = request.data
            user_instance = User.objects.create(
                username=data.get("username")                
            )
            user_instance.set_password(data.get("password"))
            user_instance.save()
            token = encode_jwt(data={
                "username": user_instance.username
            }, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTS))
            return Response({
                "access_token": token
            }, status=200)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=500)
        

class ProfileViewSet(ViewSet):
    permission_classes = [JWTAuth]

    @swagger_auto_schema(
        responses={
            200: UserSerializer(),
            400: openapi.Response(description="Name parameter is required"),
            403: openapi.Response(description="No token provided"),
            500: openapi.Response(description="Internal Server Error")
        }
    )
    @action(detail=False, methods=["get"], url_path="me", url_name="me")
    def get_profile(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=500)