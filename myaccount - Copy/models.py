from datetime import timezone
from ipaddress import summarize_address_range
from django.db.models import Q
import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.contrib.auth import get_user_model

Myuser = get_user_model

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,email,full_name,phone,password=None,password2=None):
        if not email:
            raise ValueError('Users must have an email address')
        user=self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone=phone
        
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,full_name,phone,password=None):
        user=self.create_user(
            email,
            password=password,
            full_name=full_name,
            phone=phone
        )
        user.is_admin=True
        user.save(using=self._db)
        return user

class Myuser(AbstractBaseUser):
    email=models.EmailField(verbose_name='Email',max_length=255,unique=True)
    full_name=models.CharField(max_length=200)
    phone=models.CharField(max_length=10)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    objects=UserManager()
    USERNAME_FIELD='email'
    REQUIRED_FIELDS= ['full_name','phone']

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin

class Email_verification(models.Model):
    email=models.EmailField(max_length=200,unique=True)
    otp=models.CharField(max_length=200 ,null=True, blank=True)
    is_verified=models.BooleanField(default=False)

class Phone_verification(models.Model):
    phone=models.CharField(max_length=12,unique=True)
    otp=models.CharField(max_length=6)
    is_phone_verified=models.BooleanField(default=False)

banks= (
    ("Central Bank Of India","Central Bank Of India"),
    ("State Bank Of India","State Bank Of India"),
    ("HDFC","HDFC"),
    ("Punjab National Bank ","Punjab National Bank "),
    ("Bank Of Baroda","Bank Of Baroda")
)

class Bank(models.Model):
    bank_name = models.CharField(max_length=100,choices=banks)
    account_number = models.CharField(max_length=20,unique=True)
    re_enter_account_number = models.CharField(max_length=20)
    ifsc = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)

relation = (
    ("Father","Father"),
    ("Mother","Mother"),
    ("Retired","Retired"),
    ("Self Employed","Self Employed"),
    ("Student","Student"),
    ("Unemployed","Unemployed"),
    ("Housewife","Housewife"),

)

class Nominee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile = models.IntegerField()
    date_of_birth = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    nominee_proof_identy = models.FileField()
    relation_with_nominee = models.CharField(max_length=100,choices=relation)
    percentage_of_share = models.CharField(max_length=6)

profession1 = (
    ("Salaried","Salaried"),
    ("Buisiness","Buisiness"),
    ("Retired","Retired"),
    ("Self Employed","Self Employed"),
    ("Student","Student"),
    ("Unemployed","Unemployed"),
    ("Housewife","Housewife"),

)

class KYC(models.Model):
    aadharcard_no=models.CharField(max_length=12,unique=True)
    name=models.ForeignKey(Myuser,on_delete=models.CASCADE)
    date_of_birth=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    marritul_status=models.CharField(max_length=50)
    profession=models.CharField(max_length=50,choices=profession1)
    sub_profession=models.CharField(max_length=50)
    annual_income=models.CharField(max_length=20)
    fathers_name=models.CharField(max_length=100)
    mothers_name=models.CharField(max_length=100)
    permanent_address=models.CharField(max_length=255)
    pancard_no=models.CharField(max_length=20,unique=True)

class Aadharcard_verification(models.Model):
    aadhar_no=models.CharField(max_length=12,unique=True)
    otp=models.CharField(max_length=6)
    is_aadhar_verified=models.BooleanField(default=False)

class Watchlist(models.Model):
    company_name=models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, null=True, blank=True)
    watchlist1 = models.CharField(max_length=20)
    watchlist2 = models.CharField(max_length=20)
    created_at=models.DateField(auto_now_add=True)
    

    def __str__(self):
        return "{}".format(self.company_name)

class Orders(models.Model):

    stock_exchange=(
        ("NSE","NSE"),
        ("BSE","BSE")
    )

    val=(
        ("Day","Day"),
        ("IOC","IOC")
    )
    products=(
        ("Intraday","Intraday"),
        ("Longterm","Longterm")
    )


    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, null=True, blank=True)
    lists = models.ForeignKey(Watchlist, on_delete=models.CASCADE, null=True, blank=True)
    product=models.CharField(max_length=250, choices=products)
    stock=models.CharField(max_length=250, choices=stock_exchange)
    quantity=models.IntegerField()
    price=models.FloatField(max_length=250)
    ltp=models.IntegerField() #Last Traded Price
    validity=models.CharField(max_length=250, choices=val)
    created_at=models.DateField(auto_now_add=True)  
    order_set_date = models.DateTimeField(auto_now_add=True)
    order_reach_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.stock)

class Add_Funds(models.Model): 
    made_by = models.ForeignKey(Myuser,on_delete=models.CASCADE, null=True, blank=True)
    account_balance = models.IntegerField(default='0')
    enter_amount = models.IntegerField(default='0')
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    made_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)

    def __str__(self):
  
        return "{}".format(self.made_by)

class Withdraw(models.Model):
    Total_balance = models.ForeignKey(Add_Funds,on_delete=models.CASCADE)
    amount = models.IntegerField(default='0')

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )  

