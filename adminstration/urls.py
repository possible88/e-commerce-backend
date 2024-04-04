
from django.urls import path, include

from .views import ClientAPIView

urlpatterns = [
    path('', include('common.urls')),
    path('client', ClientAPIView.as_view()),
]
