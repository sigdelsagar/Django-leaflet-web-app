from django.urls import path
from . import views
from .views import *
from django.views.generic import RedirectView
app_name = 'accounts'

urlpatterns = [

    path('api-register/', UserRegisterView.as_view()),
    path('api-login/', UserLoginAPIView.as_view()),


]
