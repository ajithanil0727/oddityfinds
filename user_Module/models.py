from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

class oddityFindsUser(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(unique=True)
    first_name      = models.CharField(max_length=30)
    last_name       = models.CharField(max_length=30)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(default=timezone.now)
    phone_number    = models.CharField(max_length=15, blank=True, null=True)
    wallet          = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    


class oddityFindsProduct(models.Model):
    proname = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dprice = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    sub_images = models.ManyToManyField('SubImage', blank=True)
    is_active = models.BooleanField(default=True)

class SubImage(models.Model):
    product =  models.ForeignKey(oddityFindsProduct, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_sub_images/')


class Category(models.Model):
    categoryname = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class CartItem(models.Model):
    user = models.ForeignKey(oddityFindsUser, on_delete=models.CASCADE)
    product = models.ForeignKey(oddityFindsProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Address(models.Model):
    user = models.ForeignKey(oddityFindsUser, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False) 

class Order(models.Model):
    user = models.ForeignKey(oddityFindsUser, on_delete=models.CASCADE) 
    order_date = models.DateTimeField(default=timezone.now)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2)     
    payment_option = models.CharField(max_length=225,default='cod')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  
    product = models.ForeignKey(oddityFindsProduct, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)  
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    is_cancel = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Cancelled', 'Cancelled'), ('Delivered', 'Delivered'), ('returned', 'returned')], default='Pending')
    

class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    offer_type = models.CharField(max_length=20,choices=[('product', 'Product-Based'), ('category', 'Category-Based')])
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    products = models.ManyToManyField(oddityFindsProduct, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    is_active = models.BooleanField(default=True)