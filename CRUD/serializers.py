from rest_framework import serializers
from .models import Hostel_info, Hostel_comment ,Image
from accounts.models import User

class Hostel_infoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hostel_info
        fields = '__all__'
        #exclude = ['id']


class Hostel_commentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hostel_comment
        fields = '__all__'
        #exclude = ['id']

class  UserSerializers(serializers.ModelSerializer):
	class Meta:
		model= User
		include=['email','password']

class  ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model= Image
        fields='__all__'