from io import BytesIO
from rest_framework import serializers
from core.models import CheckPayment, Comment, CurrencyName, ForgetPassword, Job, Message, Notice, Payment, Product, ProductComment, ProductImg, SearchProduct, User, ViewJob, ViewPost
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Corrected field declaration
        extra_kwargs = {
            'password': {'write_only': True}  # Corrected write_only key
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
 

class ProductImgSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImg
        fields = "__all__"


class CurrencyNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurrencyName
        fields = "__all__"

    
class ProductSerializer(serializers.ModelSerializer):
    images =  ProductImgSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )
    class Meta:
        model = Product
        fields = ["id", "user_id", "first_name", "last_name", "email", "phone", "likes",
                  "views","share_by", "created_at", "deleted", "Category", "Title", "Description",
                  "Itemcondition","City","State", "Country", "Price", "Negotiation", "Brand", "images",
                  "uploaded_images", "AD_payment"]
 
 