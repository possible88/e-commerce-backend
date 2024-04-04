from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have an password')
        
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = False
        user.is_staff = False
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have an password')
        
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = True
        user.is_User = False
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='defualtpics', default='defualtpics/index5.png', blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True)
    skill = models.CharField(max_length=255)
    about_me = models.CharField(max_length=255)
    is_User = models.BooleanField(default=True)
    num_Like = models.IntegerField(null=True)
    num_Post = models.IntegerField(null=True)
    isClose = models.BooleanField(default=False)
    token = models.CharField(max_length=6, blank=True, null=True)
    verified = models.BooleanField(default=False)
    AD_payment = models.BooleanField(default=False)
    AD_Period = models.CharField(max_length=255)
    currencyName = models.CharField(max_length=255)


    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()



class ForgetPassword(models.Model):
    user_id= models.IntegerField(null=True)
    email = models.EmailField(max_length=255)
    token = models.CharField(max_length=255, blank=True, null=True)


class CurrencyName(models.Model):
    currencyName = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    Price = models.CharField(max_length=15)



class ProductManager(models.Manager):
    pass

class Product(models.Model):
    user_id= models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    likes = models.IntegerField(null=True)
    views = models.IntegerField(null=True)
    share_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    Category = models.CharField(max_length=255)
    Title = models.CharField(max_length=255)
    Description = models.CharField(max_length=255)
    Itemcondition = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    State = models.CharField(max_length=255)
    Country = models.CharField(max_length=255)
    Price = models.CharField(max_length=15)
    Negotiation = models.CharField(max_length=3)
    Brand = models.CharField(max_length=255)
    AD_payment = models.BooleanField(default=False)

    objects: ProductManager = models.Manager()


class ProductImg(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='media', blank=True, null=True)

class SearchProduct(models.Model):

    user_id= models.IntegerField(null=True)
    search_name = models.CharField(max_length=255)

class ViewPost(models.Model):
     
    user_id= models.IntegerField(null=True)
    product_id= models.IntegerField(null=True)

class Job(models.Model):
    user_id= models.IntegerField(null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    likes = models.IntegerField(null=True)
    views = models.IntegerField(null=True)
    share_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    Title = models.CharField(max_length=255)
    Description = models.CharField(max_length=255)
    Company = models.CharField(max_length=255)
    Website = models.CharField(max_length=255)
    Period = models.CharField(max_length=255)
    JobNature = models.CharField(max_length=255)
    Skill = models.CharField(max_length=255)
    Education = models.CharField(max_length=255)
    State = models.CharField(max_length=255)
    Country = models.CharField(max_length=255)
    Payment = models.CharField(max_length=15)
    AD_payment = models.BooleanField(default=False)
class ViewJob(models.Model):
     
    user_id= models.IntegerField(null=True)
    job_id= models.IntegerField(null=True)



class Comment(models.Model):

    user_id= models.IntegerField(null=True)
    PostedBy_id= models.IntegerField(null=True)
    Body = models.CharField(max_length=255)
    PostedBy = models.CharField(max_length=255)
    PostedTo = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductComment(models.Model):

    product_id= models.IntegerField(null=True)
    user_id= models.IntegerField(null=True)
    PostedBy_id= models.IntegerField(null=True)
    Body = models.CharField(max_length=255)
    PostedBy = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    Category = models.CharField(max_length=255)
    Title = models.CharField(max_length=255)




class Message(models.Model):

    user_id= models.IntegerField(null=True)
    Body = models.CharField(max_length=255)
    UserTo = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    UserFrom = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    opened = models.BooleanField(default=False)


class Notice(models.Model):

    UserFrom = models.CharField(max_length=255)
    UserTo_id = models.IntegerField(null=True)
    Name = models.CharField(max_length=255)
    Message = models.CharField(max_length=255)
    Link = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    opened = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)


class Payment(models.Model):

    user_id= models.IntegerField(null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    Period = models.CharField(max_length=255)
    start_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    check_payment = models.CharField(max_length=255)


class CheckPayment(models.Model):

    user_id= models.IntegerField(null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    Period = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='payment', blank=True, null=True)
    Price = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

