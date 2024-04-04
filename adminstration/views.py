from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from common.serializer import UserSerializer

from core.models import User
# Create your views here.

class ClientAPIView(APIView):
    def get(self, _):
        clients = User.objects.filter(is_User= True)
        serializer = UserSerializer(clients, many=True)
        return Response(serializer.data)
