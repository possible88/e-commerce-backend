from datetime import datetime, timedelta
from django.utils import timezone
import string
from rest_framework import exceptions, generics, mixins

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

import random

from core.models import CheckPayment, Comment, CurrencyName, ForgetPassword, Job, Message, Notice, Payment, Product, ProductComment, User, ViewJob, ViewPost

from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from twilio.rest import Client

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.core.mail import send_mail

from django.db import models
from django.db.models import Max, OuterRef, Subquery, F
from collections import defaultdict

from JobertradeOnline.settings import DEFAULT_FROM_EMAIL
from .serializer import CheckPaymentSerializer, CommentSerializer, ForgetPasswordSerializer, JobSerializer, MessageSerializer, NoticeSerializer, PaymentSerializer, ProductCommentSerializer, ProductSerializer, SearchSerializer, UserSerializer, ViewJobSerializer, ViewSerializer

from .authentication import JWTAuthentication



# Create your views here.

class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        password = data['password']

        if len(password) < 8:
            raise exceptions.APIException(
                "Password must be at least 8 characters long.")
        if not any(c.isalpha() for c in password):
            raise exceptions.APIException("Password must contain letters.")
        if not any(c.isdigit() for c in password):
            raise exceptions.APIException("Password must contain digits.")
        # if not any(c.isupper() for c in password):
        #    raise exceptions.APIException("Password must contain uppercase letters.")

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('password do not match')

        email = data['email']

        email_validator = EmailValidator()

        try:
            email_validator(email)
        except ValidationError:
            raise exceptions.APIException('Email is not valid')

        firstname = data['first_name']
        lastname = data['last_name']

        base_username = f"{firstname.lower()}{lastname.lower()}"

        random_part = ''.join(random.choices('0123456789', k=4))
        username = f"{base_username}{random_part}"

        data['username'] = username
        data['num_Like'] = 0
        data['num_Post'] = 0
        data['skill'] = "Add Skill"
        data['about_me'] = "About Me"
        data['AD_Period'] = "None"
        data['AD_payment'] = "No"
        data['currencyName'] = "dollar"


        data['is_User'] = 'api/client' in request.path

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email, isClose=False).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect Password!')

        scope = 'client' if 'api/client' in request.path else 'admin'

        if user.is_User and scope == 'admin':
            raise exceptions.AuthenticationFailed('unauthorized')

        token = JWTAuthentication.generate_jwt(user.id, scope)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, _):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }
        return response


class EditProfileImageAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EditProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EditPasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        data = request.data

        password = data['password']

        if len(password) < 8:
            raise exceptions.APIException(
                "Password must be at least 8 characters long.")
        if not any(c.isalpha() for c in password):
            raise exceptions.APIException("Password must contain letters.")
        if not any(c.isdigit() for c in password):
            raise exceptions.APIException("Password must contain digits.")
        # if not any(c.isupper() for c in password):
        #    raise exceptions.APIException("Password must contain uppercase letters.")

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match!')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data, status=201)


class AllUsersAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)

    def delete(self, request, pk=None):
        return self.destroy(request, pk)

# Product View


class CreateProductAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # Get the logged-in user
        user = request.user
        product_data = request.data  # Separate data for the product

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        

        # Create data for the new product
        product_data['user_id'] = user_info.id
        product_data['first_name'] = user_info.first_name
        product_data['last_name'] = user_info.last_name
        product_data['email'] = user_info.email
        product_data['phone'] = user_info.phone
        product_data['likes'] = 0
        product_data['views'] = 0
        product_data['share_by'] = "null"
        product_data['AD_payment'] = user_info.AD_payment


        print(user_info.AD_payment, "12")

        # Create product serializer
        product_serializer = ProductSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()

        post = User.objects.get(id=user_info.id)
        print(post)
        post.num_Post += 1
        post.save()

        return Response({
            "product_data": product_serializer.data,
        }, status=201)  # Use 201 for resource creation


class PostAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):

        user = self.request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        

        queryset = Product.objects.filter(deleted=False).order_by(
            '-id')  # Fix this line to query Product objects
        category = self.request.query_params.get('category', '')
        description = self.request.query_params.get('description', '')
        title = self.request.query_params.get('title', '')
        itemcondition = self.request.query_params.get('itemcondition', '')
        city = self.request.query_params.get('city', '')
        state = self.request.query_params.get('state', '')
        country = self.request.query_params.get('country', '')
        brand = self.request.query_params.get('brand', '')
        userid = self.request.query_params.get('userid', '')

        if category:
            queryset = queryset.filter(Category__icontains=category)
        if description:
            queryset = queryset.filter(Description__icontains=description)
        if title:
            queryset = queryset.filter(Title__icontains=title)
        if itemcondition:
            queryset = queryset.filter(Itemcondition__icontains=itemcondition)
        if city:
            queryset = queryset.filter(City__icontains=city)
        if state:
            queryset = queryset.filter(State__icontains=state)
        if country:
            queryset = queryset.filter(Country__icontains=country)
        if brand:
            queryset = queryset.filter(Brand__icontains=brand)
        if userid:
            queryset = queryset.filter(user_id__icontains=userid)

        # Modify the Price field in the queryset
        converted_queryset = []
        for product in queryset:
            try:
                currency_now = CurrencyName.objects.get(currencyName=user_info.currencyName)
                converted_price = float(product.Price) * float(currency_now.Price)
                print(product.Price)
                print(currency_now.Price)
                print(converted_price)
                formatted_price = f"{currency_now.symbol}{converted_price:.2f}"
                product.Price = formatted_price
                converted_queryset.append(product)
            except CurrencyName.DoesNotExist:
                # Handle case where currency is not found
                pass

        return queryset

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)

    # def delete(self, request, pk=None):
    #     return self.destroy(request, pk)

