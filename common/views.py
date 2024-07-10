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

class PostDetailAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer


    def get(self, request, id):
        user = self.request.user
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        
        queryset = Product.objects.filter(id=id, deleted=False).order_by(
            '-id')
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

        serialized_data = self.serializer_class(converted_queryset, many=True).data
        return Response(serialized_data)

    # def delete(self, request, pk=None):
    #     return self.destroy(request, pk)


class SearchProductAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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

        # Create product serializer
        product_serializer = SearchSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()
        return Response({
            "product_data": product_serializer.data,
        }, status=201)  # Use 201 for resource creation


class ViewpostAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        post_data = request.data  # Separate data for the post
        producted_id = request.data.get('product_id')

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new post
        post_data['user_id'] = user_info.id

        # Create post serializer
        post_serializer = ViewSerializer(data=post_data)
        if not post_serializer.is_valid():
            return Response({"error": post_serializer.errors}, status=400)

        # Save the post
        post_serializer.save()
        # Update Posts model for view
        post = Product.objects.get(id=producted_id)
        print(post)
        post.views += 1
        post.save()
        return Response({
            "post_data": post_serializer.data,
        }, status=201)


class ViewItemAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Product.objects.none()  # Return an empty queryset if the user is not found

        view_posts = ViewPost.objects.filter(user_id=user_info.id)

        # Extract the product IDs from the view_posts queryset
        product_ids = [view_post.product_id for view_post in view_posts]

        # Return a queryset of products filtered by the extracted product IDs
        queryset = Product.objects.filter(id__in=product_ids, deleted=False).order_by('-id')
    
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


# Job View

class CreateJobAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        Job_data = request.data  # Separate data for the Job

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new Job
        Job_data['user_id'] = user_info.id
        Job_data['first_name'] = user_info.first_name
        Job_data['last_name'] = user_info.last_name
        Job_data['email'] = user_info.email
        Job_data['phone'] = user_info.phone
        Job_data['likes'] = 0
        Job_data['views'] = 0
        Job_data['share_by'] = "null"
        Job_data['AD_payment'] = user_info.AD_payment

        # Create Job serializer
        Job_serializer = JobSerializer(data=Job_data)
        if not Job_serializer.is_valid():
            return Response({"error": Job_serializer.errors}, status=400)

        # Save the Job
        Job_serializer.save()

        post = User.objects.get(id=user_info.id)
        print(post)
        post.num_Post += 1
        post.save()

        return Response({
            "Job_data": Job_serializer.data,
        }, status=201)  # Use 201 for resource creation


class JobAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):

        user = self.request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        

        queryset = Job.objects.filter(deleted=False).order_by(
            '-id')  # Fix this line to query Product objects
        company = self.request.query_params.get('company', '')
        description = self.request.query_params.get('description', '')
        title = self.request.query_params.get('title', '')
        skill = self.request.query_params.get('skill', '')
        education = self.request.query_params.get('education', '')
        state = self.request.query_params.get('state', '')
        country = self.request.query_params.get('country', '')
        jobnature = self.request.query_params.get('jobnature', '')
        userid = self.request.query_params.get('userid', '')

        if company:
            queryset = queryset.filter(Company__icontains=company)
        if description:
            queryset = queryset.filter(Description__icontains=description)
        if title:
            queryset = queryset.filter(Title__icontains=title)
        if skill:
            queryset = queryset.filter(Skill__icontains=skill)
        if education:
            queryset = queryset.filter(Education__icontains=education)
        if state:
            queryset = queryset.filter(State__icontains=state)
        if country:
            queryset = queryset.filter(Country__icontains=country)
        if jobnature:
            queryset = queryset.filter(JobNature__icontains=jobnature)
        if userid:
            queryset = queryset.filter(user_id__icontains=userid)

        # Modify the Price field in the queryset
        converted_queryset = []
        for job in queryset:
            try:
                currency_now = CurrencyName.objects.get(currencyName=user_info.currencyName)
                converted_price = float(job.Payment) * float(currency_now.Price)
                print(job.Payment)
                print(currency_now.Price)
                print(converted_price)
                formatted_price = f"{currency_now.symbol}{converted_price:.2f}"
                job.Payment = formatted_price
                converted_queryset.append(job)
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


class SearchJobAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        Job_data = request.data  # Separate data for the Job

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new Job
        Job_data['user_id'] = user_info.id

        # Create Job serializer
        Job_serializer = SearchSerializer(data=Job_data)
        if not Job_serializer.is_valid():
            return Response({"error": Job_serializer.errors}, status=400)

        # Save the Job
        Job_serializer.save()
        return Response({
            "Job_data": Job_serializer.data,
        }, status=201)  # Use 201 for resource creation


class ViewJobAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        post_data = request.data  # Separate data for the post
        Job_id = request.data.get('job_id')

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new post
        post_data['user_id'] = user_info.id

        # Create post serializer
        post_serializer = ViewJobSerializer(data=post_data)
        if not post_serializer.is_valid():
            return Response({"error": post_serializer.errors}, status=400)

        # Save the post
        post_serializer.save()
        # Update Posts model for view
        post = Job.objects.get(id=Job_id)
        print(post)
        post.views += 1
        post.save()
        return Response({
            "post_data": post_serializer.data,
        }, status=201)


class ViewJobItemAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Job.objects.none()  # Return an empty queryset if the user is not found

        view_posts = ViewJob.objects.filter(user_id=user_info.id)

        print(view_posts)

        # Extract the job IDs from the view_posts queryset
        job_ids = [view_post.job_id for view_post in view_posts]

        # Return a queryset of job filtered by the extracted job IDs
        return Job.objects.filter(id__in=job_ids, deleted=False).order_by('-id')

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)
    # def delete(self, request, pk=None):
    #     return self.destroy(request, pk)


# not login

class NotPostAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = ProductSerializer

    def get_queryset(self):

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

        converted_queryset = []
        for product in queryset:
            try:
                currency_now = CurrencyName.objects.get(currencyName="dollar")
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


class NotJobAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = JobSerializer

    def get_queryset(self):

        queryset = Job.objects.filter(deleted=False).order_by(
            '-id')  # Fix this line to query Product objects
        company = self.request.query_params.get('company', '')
        description = self.request.query_params.get('description', '')
        title = self.request.query_params.get('title', '')
        skill = self.request.query_params.get('skill', '')
        education = self.request.query_params.get('education', '')
        state = self.request.query_params.get('state', '')
        country = self.request.query_params.get('country', '')
        jobnature = self.request.query_params.get('jobnature', '')
        userid = self.request.query_params.get('userid', '')

        if company:
            queryset = queryset.filter(Company__icontains=company)
        if description:
            queryset = queryset.filter(Description__icontains=description)
        if title:
            queryset = queryset.filter(Title__icontains=title)
        if skill:
            queryset = queryset.filter(Skill__icontains=skill)
        if education:
            queryset = queryset.filter(Education__icontains=education)
        if state:
            queryset = queryset.filter(State__icontains=state)
        if country:
            queryset = queryset.filter(Country__icontains=country)
        if jobnature:
            queryset = queryset.filter(JobNature__icontains=jobnature)
        if userid:
            queryset = queryset.filter(user_id__icontains=userid)

        converted_queryset = []
        for job in queryset:
            try:
                currency_now = CurrencyName.objects.get(currencyName="dollar")
                converted_price = float(job.Payment) * float(currency_now.Price)
                print(job.Payment)
                print(currency_now.Price)
                print(converted_price)
                formatted_price = f"{currency_now.symbol}{converted_price:.2f}"
                job.Payment = formatted_price
                converted_queryset.append(job)
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

 # phone verification


class SendVerificationToken(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Generate a 6-digit random token
        token = str(random.randint(100000, 999999))
        phone = user_info.phone
        print(token, user_info.phone)

        # Send the token via SMS
        client = Client('AC39b46121df9558cb03e12217af8124a4',
                        '9e07f83c93b936d3b69d453f2246e80c')
        client.messages.create(
            body=f'Your verification token is: {token}',
            from_='+12568671602',
            to={phone}
        )

        # Update the user's token
        user_info.token = token
        user_info.save()

        # Serialize the user data and return it in the response
        serializer = UserSerializer(user_info)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerificationToken(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        phone = user_info.phone
        token = request.data.get('token')

        print(token, phone)

        try:
            verification = User.objects.get(
                phone=phone, token=token, verified=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid token or phone number'}, status=status.HTTP_400_BAD_REQUEST)

    # Mark the phone number as verified
        verification.verified = True
        verification.save()

        return Response({'message': 'Phone number verified successfully'}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):

    def post(self, request):
        email = request.data.get('email')
        user_data = request.data
        print(email)
        try:
            user = User.objects.get(email=email, isClose=False)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        print(user.email)

        # Generate a token for this user
        token = str(random.randint(100000, 999999))
        print(token)
        print(user.id)


        password_reset_url = f"http://localhost:3000/forgot/{user.id}/{token}/"

        print(password_reset_url)

        # Send a password reset email
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link below to reset your password:\n{password_reset_url}',
            from_email=DEFAULT_FROM_EMAIL,  # Use the default sender specified in Django settings
            recipient_list=[email],
        )

        try:
            forget = ForgetPassword.objects.get(user_id=user.id)
        except ForgetPassword.DoesNotExist:
            forget = None

       
        user_data = {
            'user_id': user.id,
            'email': user.email,
            'token': token,
        }
        
        print(user.id)
        print(token)
        # Create forget serializer
        user_serializer = ForgetPasswordSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({"error": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Save the forget
        user_serializer.save()

        if forget:
            forget.delete()

        return Response({'message': 'Password reset Email sent'})

class PasswordResetConfirmView(APIView):
    def put(self, request, user_id, token):
        
        data = request.data
        print(user_id)
        print(token)

        try:
            user = User.objects.get(id=user_id, isClose=False)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            forget = ForgetPassword.objects.get(user_id=user_id, token=token)
        except ForgetPassword.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        password = request.data.get('password')
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
        user.set_password(password)
        user.save()
        forget.delete()
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


class CreateCommentAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        user_data = request.data  # Separate data for the user
        comment_data = request.data  # Separate data for the user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new user
        user_data['user_id'] = user_info.id
        user_data['PostedBy'] = user_info.username
        user_data['Name'] = user_info.first_name + " " + user_info.last_name

        # Create user serializer
        user_serializer = CommentSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({"error": user_serializer.errors}, status=400)

        # Save the user
        user_serializer.save()
        if user_info.username != user_data['PostedTo']:
            message = f"{user_info.first_name} {user_info.last_name} comment your profile"

        # Assuming you have a 'post_id' variable
            post_id = int(user_data['PostedBy_id'])
            post = f"/profile/{user_data['PostedTo']}/{post_id}"

            link = post

        # Create data for the new comment
            comment_data['UserFrom'] = user_info.username
            comment_data['UserTo_id'] = user_data['PostedBy_id']
            comment_data['Message'] = message
            comment_data['Name'] = user_info.first_name + \
                " " + user_info.last_name
            comment_data['Link'] = link

        # Create comment serializer
            comment_serializer = NoticeSerializer(data=comment_data)
            if not comment_serializer.is_valid():
                return Response({"error": comment_serializer.errors}, status=400)

        # Save the user
            comment_serializer.save()

        return Response({
            "user_data": user_serializer.data if user_serializer else None,
            # Check if comment_serializer is defined
            "comment_data": comment_serializer.data if 'comment_serializer' in locals() else None,
        }, status=201)  # Use 201 for resource creation


class ViewCommentAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):

        PostedTo = self.request.query_params.get('PostedTo')
        queryset = Comment.objects.filter(PostedTo=PostedTo).order_by(
            '-id')  # Fix this line to query Product objects
        return queryset

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)


class CreateProductCommentAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        user_data = request.data  # Separate data for the user
        comment_data = request.data  # Separate data for the user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new user
        user_data['user_id'] = user_info.id
        user_data['PostedBy'] = user_info.username
        user_data['Name'] = user_info.first_name + " " + user_info.last_name

        # Create user serializer
        user_serializer = ProductCommentSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({"error": user_serializer.errors}, status=400)

        # Save the user
        user_serializer.save()

        if user_info.id != user_data['PostedBy_id']:
            message = f"{user_info.first_name} {user_info.last_name} comment your product {user_data['Title']}"

        # Assuming you have a 'post_id' variable
            post_id = int(user_data['product_id'])
            post = f"/{user_data['Category']}/{post_id}/{user_data['Title']}"

            link = post

        # Create data for the new comment
            comment_data['UserFrom'] = user_info.username
            comment_data['UserTo_id'] = user_data['PostedBy_id']
            comment_data['Message'] = message
            comment_data['Name'] = user_info.first_name + \
                " " + user_info.last_name
            comment_data['Link'] = link

        # Create comment serializer
            comment_serializer = NoticeSerializer(data=comment_data)
            if not comment_serializer.is_valid():
                return Response({"error": comment_serializer.errors}, status=400)

        # Save the user
            comment_serializer.save()

        return Response({
            "user_data": user_serializer.data if user_serializer else None,
            # Check if comment_serializer is defined
            "comment_data": comment_serializer.data if 'comment_serializer' in locals() else None,
        }, status=201)  # Use 201 for resource creation


class ViewProductCommentAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductCommentSerializer

    def get_queryset(self):

        product_id = self.request.query_params.get('product_id')
        print(product_id + "go")
        queryset = ProductComment.objects.filter(product_id=product_id).order_by(
            '-id')  # Fix this line to query Product objects
        return queryset

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)


class CreateMessageAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user
        user_data = request.data  # Separate data for the user
        comment_data = request.data  # Separate data for the user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Create data for the new user
        user_data['user_id'] = user_info.id
        user_data['UserFrom'] = user_info.email
        user_data['Name'] = user_info.first_name + " " + user_info.last_name

        # Create user serializer
        user_serializer = MessageSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({"error": user_serializer.errors}, status=400)

        # Save the user
        user_serializer.save()

        if user_info.id != user_data['UserTo']:
            message = f"{user_info.first_name} {user_info.last_name} send you a new message"

        # Assuming you have a 'post_id' variable
            post_id = int(user_info.id)
            post = f"/message/{post_id}"

            link = post

        # Create data for the new comment
            comment_data['UserFrom'] = user_info.username
            comment_data['UserTo_id'] = user_data['UserTo']
            comment_data['Message'] = message
            comment_data['Name'] = user_info.first_name + \
                " " + user_info.last_name
            comment_data['Link'] = link

        # Create comment serializer
            comment_serializer = NoticeSerializer(data=comment_data)
            if not comment_serializer.is_valid():
                return Response({"error": comment_serializer.errors}, status=400)

        # Save the user
            comment_serializer.save()

        return Response({
            "user_data": user_serializer.data if user_serializer else None,
            # Check if comment_serializer is defined
            "comment_data": comment_serializer.data if 'comment_serializer' in locals() else None,
        }, status=201)  # Use 201 for resource creation


class ViewMessageAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        UserTo = self.request.query_params.get('UserTo')
        user_id = self.request.user.id  # Assuming you have a logged-in user

        queryset = Message.objects.filter(
            (models.Q(user_id=user_id, UserTo=UserTo) |
             models.Q(user_id=UserTo, UserTo=user_id))
        ).order_by('id')

        return queryset

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)


class GetUnreadNumberNotice(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NoticeSerializer

    def get_queryset(self):
        UserTo_id = self.request.query_params.get('UserTo_id')

        queryset = Notice.objects.filter(
            UserTo_id=UserTo_id, opened=False).order_by('-id')

        return queryset

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)


class MessageAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        User2 = self.request.query_params.get('UserTo')
        user_id = self.request.user.id  # Assuming you have a logged-in user

        print(User2)
        print(user_id)

                # Assuming you have a queryset like this
        queryset = Message.objects.filter(UserTo=User2).order_by('id')

        # Fetch all messages into a list
        messages = list(queryset)

        # Create a dictionary to store unique messages based on user_id
        unique_messages = defaultdict(list)

        for message in messages:
            unique_messages[message.user_id].append(message)

        # Get the latest message for each user_id
        latest_messages = [messages[-1] for messages in unique_messages.values()]

        return latest_messages

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        return self.list(request)


class MonthPaymentPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        # user = request.user
        product_data = request.data  # Separate data for the product

        email = product_data['email']
        payments = product_data['check_payment']

        # Fetch user information from the database
        try:
            user_info = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        
        try:
            Check_Payment = Payment.objects.get(user_id=user_info.id, active=True)
        except Payment.DoesNotExist:
            Check_Payment = None

        if Check_Payment and Check_Payment.user_id > 0:
            return Response({'error': 'User already has a active Account'}, status=status.HTTP_400_BAD_REQUEST)

        
        # Get the current date and time
        start_time = datetime.now()

# Calculate the end time by adding one month
        end_time = start_time + timedelta(days=30)

        # Create data for the new product
        product_data['user_id'] = user_info.id
        product_data['first_name'] = user_info.first_name
        product_data['last_name'] = user_info.last_name
        # product_data['email'] = user_info.email
        product_data['Period'] = "Month"
        product_data['end_at'] = end_time

        # Create product serializer
        product_serializer = PaymentSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()

        payment = User.objects.get(id=user_info.id)
        payment.AD_Period = product_data['Period']
        payment.AD_payment = True

        payment.save()

        create_payments = CheckPayment.objects.get(user_id=user_info.id, id=payments)
        create_payments.approved = True

        create_payments.save()

        return Response({
            "product_data": product_serializer.data,
        }, status=201)  # Use 201 for resource creation


class TwoWeeksPaymentPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        # user = request.user
        product_data = request.data  # Separate data for the product

        email = product_data['email']
        payments = product_data['check_payment']

        # Fetch user information from the database
        try:
            user_info = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        
        try:
            Check_Payment = Payment.objects.get(user_id=user_info.id, active=True)
        except Payment.DoesNotExist:
            Check_Payment = None

        if Check_Payment and Check_Payment.user_id > 0:
            return Response({'error': 'User already has a active Account'}, status=status.HTTP_400_BAD_REQUEST)

        
        # Get the current date and time
        start_time = datetime.now()

# Calculate the end time by adding one month
        end_time = start_time + timedelta(days=14)

        # Create data for the new product
        product_data['user_id'] = user_info.id
        product_data['first_name'] = user_info.first_name
        product_data['last_name'] = user_info.last_name
        # product_data['email'] = user_info.email
        product_data['Period'] = "TwoWeeks"
        product_data['end_at'] = end_time

        # Create product serializer
        product_serializer = PaymentSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()

        payment = User.objects.get(id=user_info.id)
        payment.AD_Period = product_data['Period']
        payment.AD_payment = Trueg

        payment.save()

        create_payments = CheckPayment.objects.get(user_id=user_info.id, id=payments)
        create_payments.approved = True

        create_payments.save()


        return Response({
            "product_data": product_serializer.data,
        }, status=201)  # Use 201 for resource creation


class OneWeekPaymentPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        # user = request.user
        product_data = request.data  # Separate data for the product

        email = product_data['email']
        payments = product_data['check_payment']

        # Fetch user information from the database
        try:
            user_info = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        
        try:
            Check_Payment = Payment.objects.get(user_id=user_info.id, active=True)
        except Payment.DoesNotExist:
            Check_Payment = None

  

        if Check_Payment and Check_Payment.user_id > 0:
            return Response({'error': 'User already has a active Account'}, status=status.HTTP_400_BAD_REQUEST)

        
        # Get the current date and time
        start_time = datetime.now()

# Calculate the end time by adding one month
        end_time = start_time + timedelta(days=7)

        # Create data for the new product
        product_data['user_id'] = user_info.id
        product_data['first_name'] = user_info.first_name
        product_data['last_name'] = user_info.last_name
        # product_data['email'] = user_info.email
        product_data['Period'] = "OneWeek"
        product_data['end_at'] = end_time

        # Create product serializer
        product_serializer = PaymentSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()

        payment = User.objects.get(id=user_info.id)
        payment.AD_Period = product_data['Period']
        payment.AD_payment = True

        payment.save()
        
        print(user_info.id)

        create_payments = CheckPayment.objects.get(user_id=user_info.id, id=payments)
        create_payments.approved = True

        create_payments.save()


        return Response({
            "product_data": product_serializer.data,
        }, status=201)  # Use 201 for resource creation


class ActiveAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        
        try:
            check_payment = Payment.objects.get(user_id=user.id, active=True)
        except Payment.DoesNotExist:
            check_payment = None

         # Get the current date and time
        start_time = timezone.now()
        # print(user_info.id)
        # print(start_time)
        # print(check_payment.end_at)

        if check_payment and check_payment.end_at < start_time:

            payment = User.objects.get(id=user_info.id)
            payment.AD_Period = "None"
            payment.AD_payment = False

            payment.save()
            check_payment.active = False

            check_payment.save()


        return Response({
            "message": "True",
        }, status=201)  # Use 201 for resource creation


class CreatePaymentAPIView(APIView):

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

        # Create product serializer
        product_serializer = CheckPaymentSerializer(data=product_data)
        if not product_serializer.is_valid():
            return Response({"error": product_serializer.errors}, status=400)

        # Save the product
        product_serializer.save()
        return Response({
            "message": "successful",
        }, status=201)  # Use 201 for resource creation


class ActivePostAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the logged-in user
        user = request.user

        # Fetch user information from the database
        try:
            user_info = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"})

        # Check conditions
        if user_info.num_Post >= 0 and user_info.AD_payment:
            return Response({
                "message": "Active",
            }, status=201)  # Use 201 for resource creation
        if user_info.num_Post < 6 and user_info.verified :
            return Response({
                "message": "less",
            }, status=201)  # Use 201 for resource creation
        else:
            return Response({"message": "False"}, status=201)  # You can use 400 for a bad request