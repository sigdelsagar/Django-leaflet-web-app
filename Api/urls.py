from django.urls import include, path
from rest_framework import routers
from . import views
from .swagger_schema import swagger
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Hostel API')


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'hostel', views.HostelViewSet)
router.register(r'login', views.LoginView, basename='MyModel')
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls), name='rest-api'),
    # path('openapi/', TemplateView.as_view(
    #     template_name='CRUD/swagger-ui.html',
    #     extra_context={'schema_url': 'openapi-schema'}
    # ), name='swagger-ui'),
    # path('openapi/', schema_view, name='open-api'),
    path('swagger/', swagger),

    # path('example/', views.ExampleView.as_view()),
    # path('login/', obtain_auth_token, name='api-login'),


]
