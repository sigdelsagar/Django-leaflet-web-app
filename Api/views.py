from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, filters
import django_filters.rest_framework
from .serializers import *
from CRUD.models import Hostel_info
from .permissions import IsOwnerOrReadOnly
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.decorators import api_view

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # filterset_fields = ['email', ]
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     permission_classes = [IsAuthenticated]
    #     if self.action == 'list':
    #         permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    #     return [permission() for permission in permission_classes]

    # def get_object(self):
    #     obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
    #     self.check_object_permissions(self.request, obj)
    #     return obj


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        print(type(request.user))
        return queryset.filter(user_ins=request.user)


class HostelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows hostels to be viewed or edited.
    parameters:
      - name: name
        type: string
        required: true
        location: form
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    queryset = Hostel_info.objects.all()
    serializer_class = HostelSerializer
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['Hostel_name', ]
    # filter_backends = []
    ordering_fields = ['Hostel_Price', 'Hostel_name']

    def perform_create(self, serializer):
        serializer.save(user_ins=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ExampleView(APIView):
    # authentication_classes = [Ba sicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # import unicode
        content = {

            # `django.contrib.auth.User` instance.
            'user': str(request.user),
            'auth': str(request.auth),  # None
        }
        return Response(content)


class LoginView(viewsets.ViewSet):
    """ A really cool function"""
    # def list(self, request):
    #     return Response({'username': "User's email address", "password": "Users password"})

    def create(self, request):
        print(request.data)
        serializer = AuthTokenSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

@api_view(['POST'])
def save_medical(request):
    name = request.POST.get('name')
    bloodgroup = request.POST.get('bloodgroup')
    birthmark = request.POST.get('birthmark')
    try:
        Medical.objects.create(name= name, bloodgroup = bloodgroup, birthmark = birthmark)
        return Response("Data Saved!", status=status.HTTP_201_CREATED)
    except Exception as ex:
        return Response(ex, status=status.HTTP_400_BAD_REQUEST)