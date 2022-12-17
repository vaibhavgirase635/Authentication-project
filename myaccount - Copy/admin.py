from django.contrib import admin
from myaccount.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
class UserModelAdmin(BaseUserAdmin):
    list_display=['id','email','full_name','phone','is_verified']
    
    fieldsets=(
        ('User Credentials',{'fields':('email','password')}),
        ('Personal info',{'fields':('full_name','phone','is_verified')}),
        ('Permissions',{'fields':('is_admin',)})
    )

    add_fieldsets=(
        (None,{
            'classes':('wide',),
            'fields':('email','full_name','phone','password1','password2','is_verified'),
        }),
    )
    search_fields=('email',)
    ordering=('email','id')
    filter_horizontal=()

    admin.site.register(Myuser,)

admin.site.register(Email_verification)

admin.site.register(Phone_verification)

admin.site.register(Bank)

@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','last_name','email','mobile','date_of_birth','address','nominee_proof_identy','relation_with_nominee','percentage_of_share']

@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['id','aadharcard_no','name','date_of_birth','gender','marritul_status','profession','sub_profession','annual_income','fathers_name','mothers_name','permanent_address','pancard_no']

@admin.register(Aadharcard_verification)
class AadharcardAdmin(admin.ModelAdmin):
    list_display = ['id','aadhar_no','otp','is_aadhar_verified']

admin.site.register(Watchlist)

admin.site.register(Orders)

admin.site.register(Add_Funds)

admin.site.register(Withdraw)