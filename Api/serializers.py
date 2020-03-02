from rest_framework import serializers
from django.contrib.auth import get_user_model
from CRUD.models import Hostel_info

User = get_user_model()


class HostelSerializer(serializers.HyperlinkedModelSerializer):
    # user_ins = serializers.HyperlinkedRelatedField(
    #     queryset=User.objects.all(), required=False, view_name='user-detail')
    # Authorization = serializers.CharField()

    class Meta:
        model = Hostel_info
        fields = ["id", "Hostel_name", "Hostel_Price", "url"]
        # fields = "__all__"


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # hostel_info_set = serializers.StringRelatedField(many=True, read_only=True)
    # hostels = HostelSerializer(
    #     many=True, required=False, source='hostel_info_set')

    last_login = serializers.DateTimeField(
        allow_null=True, required=False, read_only=True)
    admin = serializers.BooleanField(required=False, read_only=True)
    # hostel_info_set = serializers.PrimaryKeyRelatedField(
    #     many=True, read_only=True)
    # hostels = hostel_info_set

    class Meta:
        model = User
        fields = ["id", "email", "last_login",
                  "admin"]

        extra_kwargs = {'password': {'write_only': True}
                       }
