
from xml.dom import ValidationErr
from rest_framework import serializers
from myaccount.models import Myuser
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from myaccount.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=Myuser
        fields=['email','name','password','password2','tc']
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
        fields=['id','email','name']

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
            link= 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            print('Password Reset Link',link)
            #send email
            body='click following link to reset your password' +link
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


