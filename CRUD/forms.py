from django import forms
from .models import *
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import fields, CheckboxInput
User = get_user_model()


# class Hostel_Request_Form(forms.ModelForm):
#     #Hostel_name = forms.CharField(max_length=100)
#     Hostel_Address = forms.CharField(label='Address', max_length=50)
#     Hostel_Ph_No = forms.IntegerField(label='Phone No')
#     Hostel_Mobile_No = forms.IntegerField(label='Mobile No')
#     Hostel_Price = forms.IntegerField(
#         label='Price', widget=forms.TextInput(attrs={'placeholder': '(NRs)'}))
#     Hostel_Estd = forms.DateTimeField(
#         label='Estd', widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YY'}))

#     class Meta:
#         model = Hostel_info
#         fields = '__all__'
#         labels = {
#             'Hostel_name': _('Name'),
#             'Hostel_long': _('Longitude'),
#             'Hostel_lat': _('Latitude')
#         }


class LoginForm(forms.Form):
    email = forms.CharField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))


class SignupForm(forms.ModelForm):
    email = forms.CharField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['email', ]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("email already exists")
        return email

    def clean_confirm_password(self):
        pword = self.cleaned_data["password"]
        c_pword = self.cleaned_data["confirm_password"]
        if pword != c_pword:
            raise forms.ValidationError("Password didnot match")
        return c_pword
    

Hostel_Type=[
    ('male','Male'),
    ('female','Female'),
    ('both','Both'),
]
class Hostel_Request_Form(forms.ModelForm):
    Hostel_Address = forms.CharField(label='Address', max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Chabahil,Kathmandu'}))
    Hostel_Ph_No = forms.IntegerField(label='Phone No',required=False)
    Hostel_Mobile_No = forms.CharField( max_length=50,label='Mobile No',required=False)
    Hostel_Price = forms.IntegerField(
        required=False,label='Price', widget=forms.TextInput(attrs={'placeholder': '(NRs)'}))
    Hostel_Estd = forms.DateTimeField(
        label='Estd', widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YY'}),required=False)
    image = forms.ImageField(label='Images',widget=forms.ClearableFileInput(attrs={'multiple': True}))
    Hostel_type=forms.CharField(label='Hostel Type',widget=forms.Select(choices=Hostel_Type))
    wifi=forms.BooleanField(required=False,label='wifi')
    lodging=forms.BooleanField(required=False,label='lodging')
    studyRoom=forms.BooleanField(required=False,label='studyRoom')
    laundary=forms.BooleanField(required=False,label='laundary')
    medicalFacility=forms.BooleanField(required=False,label='medicalFacility')
    singleRoom=forms.BooleanField(required=False,label='singleRoom')
    dormitory=forms.BooleanField(required=False,label='dormitory')
    # about=forms.CharField( required=False,max_length=200,label='About', widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    class Meta:
        model = Hostel_Request
        exclude = ['Hostel_lat','Hostel_long',]
        labels = {
            'Hostel_name': _('Name'),
            'Hostel_long': _('Longitude'),
            'Hostel_lat': _('Latitude')
        }
    
class Hostel_commentForm(forms.ModelForm):
    class Meta:
        fields=('comment',)
