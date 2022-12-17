from rest_framework import serializers
from myaccount.models import *
from xml.dom import ValidationErr
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from myaccount.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=Myuser
        fields=['id','email','full_name','phone','password','password2','created_at','updated_at']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        return attrs

    def create(self,validate_data):
        return Myuser.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=Myuser
        fields=['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Myuser
        fields=['id','email','full_name','phone']

class UserChangePasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields=['password','password2']

    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        user=self.context.get('user')
        if password != password2:
            raise serializers.ValidationError('Password and Password2 not match')
        user.set_password(password)
        user.save()
        return attrs

# class ChangePasswordSerializer(serializers.Serializer):
#     model = Myuser

#     """
#     Serializer for password change endpoint.
#     """
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)
    
class SendEmailResetPasswordSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        fields=['email']

    def validate(self,attrs):
        email=attrs.get('email')
        if Myuser.objects.filter(email=email).exists():
            user= Myuser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID',uid)
            token= PasswordResetTokenGenerator().make_token(user)
            print('Password reset token',token)
            link= 'http://localhost:3000/resetpassword/'+uid+'/'+token
            print('Password Reset Link',link)
            #send email
            body='click following link to reset your password' + link
            data={
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationErr('You are not a Registered User')

class UserResetPasswordSerializer(serializers.Serializer):
        password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
        password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
        class Meta:
            fields=['password','password2']
        
        def validate(self,attrs):
            try:
              password=attrs.get('password')
              password2=attrs.get('password2')
              uid=self.context.get('uid')
              token=self.context.get('token')
              if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
              id=smart_str(urlsafe_base64_decode(uid))
              user=Myuser.objects.get(id=id)
              if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationErr('Token is not valid or expired')
              user.set_password(password)
              user.save()
              return attrs
            except DjangoUnicodeDecodeError as identifier:
                PasswordResetTokenGenerator().check_token(user,token)
                raise ValidationErr('Token is not valid or expired')

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email_verification
        fields = ['email','is_verified']

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['bank_name','account_number','re_enter_account_number','ifsc','branch']

class NomineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nominee
        fields = ['id','first_name','last_name','email','mobile','date_of_birth','address','nominee_proof_identy','relation_with_nominee','percentage_of_share']

class UserKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = ['id','aadharcard_no','name','date_of_birth','gender','marritul_status','profession','sub_profession','annual_income','fathers_name','mothers_name','permanent_address','pancard_no']

class Watchlist_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields=["company_name","user","watchlist1","watchlist2","created_at"]

class Orders_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ["user", "lists", "stock" , "quantity","price","ltp","validity", "created_at","order_set_date","order_reach_date"]

class Add_Funds_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Add_Funds
        fields= ["made_by","account_balance","enter_amount","order_id","made_on",]

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = ['Total_balance','amount']
        