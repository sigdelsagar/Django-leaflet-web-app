from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from rest_framework.serializers import EmailField, CharField
from rest_framework.exceptions import ValidationError

from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from CRUD.token import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import send_mail

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print (validated_data)
        email = validated_data['email']
        password = validated_data['password']
        user_obj = User(
            email=email,   
            active=False,      
        )
        user_obj.set_password(password)
        user_obj.save()
        subject = 'Thank you for registering to our site'    
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]
       
        # current_site = get_current_site(self.request).domain
        uid = urlsafe_base64_encode(force_bytes(user_obj.pk)).decode()
        print (uid)
        token = account_activation_token.make_token(user_obj)
        message = 'Please use this link to login http://nephostel.herokuapp.com/'+'activate/'+str(uid)+'/'+str(token)+'/'
                    
        send_mail(subject, message, email_from, recipient_list)                    
        
        return validated_data


class UserLoginSerializer(serializers.ModelSerializer):
    email = EmailField(label='Email')
    password = CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password')
        # extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        user_obj = None
        email = data.get("email", None)
        password = data["password"]
        if not email:
            raise exceptions.ValidationError('Email is required to login')

        user = User.objects.filter(
            email=email
        )

        if user.exists():
            user_obj = user.first()        #gives email
        else:
            raise exceptions.ValidationError('Email is not valid')
        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credentials")
        return data
