from django.urls import include, path
from rest_framework import routers 

from myaccount.views import *

from . import views

router = routers.SimpleRouter()


urlpatterns = [
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('changepassword/',UserChangePasswordView.as_view(),name='changepassword'),
    path('send-reset-password-email/',SendEmailResetPasswordView.as_view(),name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/',UserPasswordResetView.as_view(),name='resetpassword'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('registeremail/',RegisterEmail.as_view(),name='registeremail'),
    path('verifyemail/',VerifyEmailView.as_view(),name='verifyemail'),
    path('registerphone/',views.RegisterPhoneView,name='registerphone'),
    path('verifyphone/',views.VerifyPhoneView,name='verifyphone'),
    path('bank/',BankView.as_view(),name='bank'),
    path('nominee/',NomineeView.as_view(),name='nominee'),
    path('kyc/',UserKYCView.as_view(),name='kyc'),
    path('watchlist/',Watchlist_View.as_view(),name='watchlist'),
    path('order/',Order_List.as_view(),name='order'),
    path('addfund/',Add_Fund.as_view(),name='addfund'),
    path('check/',views.Check,name='check'),
    
    path('checkout/<int:id>/',views.checkout,name='checkout'),
    path('handlerequest/', views.handlerequest),
]



