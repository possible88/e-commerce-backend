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
 
    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        product = Product.objects.create(**validated_data)

        for image in uploaded_images:
            # Open the uploaded image using Pillow
            img = Image.open(image)

            # Convert the image to RGB format (WebP requires RGB)
            img = img.convert('RGB')

            # Create a BytesIO object to store the WebP image data
            output_io = BytesIO()

            # Save the image in WebP format with the desired quality
            img.save(output_io, 'WEBP', quality=50)

            # Create a SimpleUploadedFile from the BytesIO data
            webp_image = SimpleUploadedFile(
                name=f"{image.name.replace('.jpg', '.webp')}",  # Adjust the file extension as needed
                content=output_io.getvalue(),
                content_type='image/webp'
            )

            # Create a ProductImg instance and associate it with the product
            ProductImg.objects.create(product=product, image=webp_image)

        return product
    
class SearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchProduct
        fields = "__all__"

class ViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViewPost
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = "__all__"

class ViewJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViewJob
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"

class ProductCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductComment
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"

class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = "__all__"

   
class ForgetPasswordSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = ForgetPassword
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Payment
        fields = "__all__"


class CheckPaymentSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = CheckPayment
        fields = "__all__"