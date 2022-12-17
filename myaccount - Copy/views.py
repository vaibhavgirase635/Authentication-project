
import json
from pyexpat.errors import messages
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,viewsets,generics
from rest_framework.views import APIView
from myaccount.serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view,permission_classes
from .utils import send_otp_via_email,send_otp_to_phone,send_otp_to_aadharno
from .models import *
from rest_framework.generics import GenericAPIView,ListAPIView,ListCreateAPIView
from rest_framework.mixins import CreateModelMixin
from django.shortcuts import redirect
from .permissions import *
from .checksum import *
from django.views.decorators.csrf import csrf_exempt
from .checksum import *
from rest_framework import permissions

def get_tokens_for_user(user):
    refresh=RefreshToken.for_user(user)
    return{
        'refresh':str(refresh),
        'access':str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    
    def post(self,request,format=None):
        serializer=UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            token=get_tokens_for_user(user)
            return Response({'token':token,'msg':'Registration Successful'},
            status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    
    
    def post(self,request,format=None):
        serializer=UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.data.get('email')
            password=serializer.data.get('password')
            user=authenticate(email=email,password=password)
            if user is not None:
                token=get_tokens_for_user(user)
                return Response({'token':token,'message':'Login Successfully !!'})

            else:
                return Response({'errors':{'non_field_errors':['Email or Password os not Valid']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        serializer=UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Change Successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class ChangePasswordView(generics.UpdateAPIView):
#     """
#     An endpoint for changing password.
#     """
#     serializer_class = ChangePasswordSerializer
    
#     permission_classes = (IsAuthenticated,)

#     def get_object(self, queryset=None):
#         obj = self.request.user
#         return obj

#     def update(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         serializer = self.get_serializer(data=request.data)

#         if serializer.is_valid():
#             # Check old password
#             if not self.object.check_password(serializer.data.get("old_password")):
#                 return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
#             # set_password also hashes the password that the user will get
#             self.object.set_password(serializer.data.get("new_password"))
#             self.object.save()
#             response = {
#                 'status': 'success',
#                 'code': status.HTTP_200_OK,
#                 'message': 'Password updated successfully',
#                 'data': []
#             }

#             return Response(response)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendEmailResetPasswordView(APIView):
    #renderer_classes=[UserRenderer]
    queryset = Myuser.objects.all()
    def post(self,request,format=None):
        serializer=SendEmailResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset link send.Please check your Email'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    #renderer_classes=[UserRenderer]
    def post(self,request,uid,token,format=None):
        serializer=UserResetPasswordSerializer(data=request.data,context={'uid':uid,'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset Successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request ,format=None):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RegisterEmail(APIView):
    def post(self,request):
            serializer = EmailSerializer(data = request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                send_otp_via_email(serializer.data['email']) 
                return Response({'message':'registration successful check email'},status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        try:
            serializer = VerifyEmailSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']

                user = Email_verification.objects.filter(email=email)
                if not user.exists():
                    return Response({
                        'status':400,
                        'message':'something went wrong',
                        'data':'invalid email'
                    })
                if user[0].otp != otp:
                    return Response({
                        'status':400,
                        'message':'something went wrong',
                        'data':'wrong otp'
                    })
                user=user.first()
                user.is_verified = True
                user.save()
                return Response({
                    'status':200,
                    'message':'account verified',
                    'data':{}
                })
            return Response({
                        'status':400,
                        'message':'something went wrong',
                        'data':'invalid email'
                        })

        except Exception as e:
            print(e)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def RegisterPhoneView(request):
    data = request.data
    if data.get('phone') is None:
        return Response({
            'status':400,
            'message':'key phone number is required'
        })
    user = Phone_verification.objects.create(
        phone = data.get('phone'),
        otp = send_otp_to_phone(data.get('phone'))
    )
    user.save()
    return Response({
        'status':200, 'message':'otp sent'
    })

@api_view(['POST'])
def VerifyPhoneView(request):
    data = request.data

    if data.get('phone') is None:
        return Response({
            'status':400,
            'message': 'key phone number is required'
        })
    
    if data.get('otp') is None:
        return Response({
            'status': 400,
            'message' : 'key otp is required'
        })
    try:
        user_obj = Phone_verification.objects.get(phone = data.get('phone'))

    except Exception as e:
        return Response({
            'status':400,
            'message':'invalid phone'
        })
    
    if user_obj.otp == data.get('otp'):
        user_obj.is_phone_verified=True
        user_obj.save()

        return Response({
            'status':200,
            'message': 'Mobile number verified'
        })
    return Response({
        'status':400,
        'message':'invalid otp'
    })

class BankView(CreateModelMixin, GenericAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
          return self.create(request, *args, **kwargs)


class NomineeView(CreateModelMixin, GenericAPIView):
    queryset = Nominee.objects.all()
    serializer_class = NomineeSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
          return self.create(request, *args, **kwargs)

class UserKYCView(CreateModelMixin, GenericAPIView):
    queryset =KYC.objects.all()
    serializer_class = UserKYCSerializer
    permission_classes=[AllowAny]
    def post(self, request, *args, **kwargs):
          return self.create(request, *args, **kwargs)

@api_view(['POST'])
def RegisterAadharView(request):
    data = request.data
    if data.get('aadhar_no') is None:
        return Response({
            'status':400,
            'message':'key aadhar number is required'
        })
    user = Aadharcard_verification.objects.create(
        aadhar_no = data.get('aadhar_no'),
        otp = send_otp_to_aadharno(data.get('aadhar_no'))
    )
    user.save()
    return Response({
        'status':200, 'message':'otp sent'
    })

@api_view(['POST'])
def VerifyAadharView(request):
    data = request.data

    if data.get('aahar_no') is None:
        return Response({
            'status':400,
            'message': 'key aadhar number is required'
        })
    
    if data.get('otp') is None:
        return Response({
            'status': 400,
            'message' : 'key otp is required'
        })
    try:
        user_obj = Aadharcard_verification.objects.get(aadhar_no = data.get('aadhar_no'))

    except Exception as e:
        return Response({
            'status':400,
            'message':'invalid aadhar no'
        })
    
    if user_obj.otp == data.get('otp'):
        user_obj.is_aadhar_verified=True
        user_obj.save()

        return Response({
            'status':200,
            'message': 'Aadharcard number verified'
        })
    return Response({
        'status':400,
        'message':'invalid otp'
    })

class Watchlist_View(generics.CreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = Watchlist_Serializer

    def get(self, request, format=None):
        watchlist = Watchlist.objects.all()
        serializer = Watchlist_Serializer(watchlist, many=True)
        return Response(serializer.data)

class Order_List(ListAPIView):
    serializer_class = Orders_Serializer
    permission_classes = (Is_Authenticated, IsUser)

    def get_queryset(self):
        user = self.request.user
        query = Orders.objects.filter()
        return query

class Add_Fund(ListCreateAPIView):
    queryset = Add_Funds.objects.all()
    serializer_class = Add_Funds_Serializer

def Check(request):
	return render(request, 'check.html')

def PaymentComplete(request):
	body = json.loads(request.body)
	print('BODY:', body)
	fund = Add_Funds.objects.get(id=body['add_fundsId'])
	Orders.objects.create(
		fund=fund
		)
	return JsonResponse('Payment completed!', safe=False)

def checkout(request,id):
    if request.method == "GET":
        return render(request, 'pay.html')
    try:
        enter_amount = int(request.POST['amount'])
        #orderid = str(request.POST['order_id'])
    except:
        return render(request, 'pay.html') 
    #fund = Add_Funds.objects.filter('order_id')
    #print(fund)
    print(id)
    order = Add_Funds.objects.create(account_balance=enter_amount,enter_amount=enter_amount)
    
    order.save()
    
    merchant_key = settings.PAYTM_SECRET_KEY
    params = (
        ('MID',  settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(order.order_id)),
        ('CUST_ID', 'test555666@paytm.com'),
        ('TXN_AMOUNT', str(order.enter_amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/handlerequest/'),
        )
    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)
    order.checksum = checksum
    order.save()
    obj = Add_Funds.objects.get(id=id)
    obj.account_balance += enter_amount
    obj.save()
    id = order.order_id
    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def handlerequest(request):
    queryset = Add_Funds.objects.all()
    serializer_class = Add_Funds_Serializer
    if request.method == 'POST':
        paytm_checksum = ''
        print(request.body)
        print(request.POST)
        received_data = dict(request.POST)
        print(received_data)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            print("Checksum Matched")
            received_data['message'] = "Checksum Matched"
        else:
            print("Checksum Mismatched")
            received_data['message'] = "Checksum Mismatched"

        return render(request, 'callback.html', context=received_data)
    
def Withdraw_balance(request,id):
    if request.method == "GET":
        return render(request, 'withdraw.html')
    try:
        enter_amount = int(request.POST['amount'])
        
    except:
        return render(request, 'pay.html') 
    
    print(id)
    order = Add_Funds.objects.get(id=id)
    
    order.save()

    