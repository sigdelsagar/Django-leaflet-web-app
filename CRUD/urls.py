from django.urls import path,re_path
from django.conf.urls import url
from . import views
from .views import *

app_name = 'CRUD'

urlpatterns = [

    #admin dashboard login,logout...vi
    path('search/', views.Search, name='search'),
    # path('search-user/', views.search, name='search-user'),
    path('map/', views.mapview, name='map'),
    path("login/", LoginView.as_view(), name ='login'),
    path("logout/", LogoutView.as_view(), name='logout'),

    #create ,upadte,list and delete single object
    path("main/", Hostel_CreateView.as_view(), name='add-hostel'),
    path('view/', Hostel_ListView.as_view(), name='list-hostel'),
    path('hostel-list/', Hostels.as_view(), name='hostel-list'),
    path('delete/<int:id>/', Hostel_DeleteView.as_view(), name='delete-single-hostel'),
    path('update/<int:id>/', Hostel_UpdateView.as_view(), name='update-hostel'),
    path('manageusers/', Users_ListView.as_view(), name='list-users'),
    
    #path("register/", RegisterView.as_view(),name="register"),
    #list hostel request,accept or delete request
    path('hostel-request-list/', Hostel_Request_ListView.as_view(), name='list-req-hostel'),
    path('hostel-accept/<int:pk>/', Hostel_AcceptView.accept, name='hostel-accept'),
    path('hostel-reject/<int:pk>/', Hostel_RejectView.reject, name='hostel-reject'),
    path('hostel-request-view/<int:pk>', views.hostel_DetailView, name='hostel-request-view'),

    path('delete-hostel/', DeleteGroup.deleteHostel, name='delete-hostel'),
    path('delete-user/', DeleteGroup.deleteUser, name='delete-user'),
    #Client register,create,verify,login
    #path("client-login/", ClientLoginView.as_view()),
    path("register/", ClientRegisterView.as_view(),name="register"),
    path("activation-sent/",views.verifyNotification,name='activation-sent'),
    path("client/", Client_CreateView.as_view(), name='insert'),
    path ("client-map/",views.clientmap,name="client-map"),
    
    
    #url (r"^direction/(?P<h_long>[0-9]+)/$",views.direction,name="direction"),
    path ("direction/<str:h_long>/<str:h_lat>/",views.direction, name='direction'),
    
    path("comments/", Comments.as_view(), name='comments'),
    path("comment-form/<int:id>/",views.commentform,name='commentform'),
    path('delete-comment/', DeleteGroup.deleteComment, name='delete-comment'),
    path('delete-comment-all/', DeleteGroup.deleteCommentAll, name='delete-comment-all'),
    re_path('hostel-comments/', Hostel_Comments.get, name='hostel-comments'),

    #path("user-comment/", views.comment, name='user-comment'),
    
    #sort hostel
    path("cheap-hostel/", views.cheapSortHostel, name='cheap-hostel'),
    path("expen-hostel/", views.expenSortHostel, name='expen-hostel'),
    path("boys-hostel/",views.sortMale, name='boys-hostel'),
    path("girls-hostel/",views.sortFemale, name='girls-hostel'),

    url (r"^search-hostel/$",views.searchhostel),
    path ("hostel-detail/",views.totalhostel,name="total-hostel"),
    #account activaiton link
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    #nearest
    path ("nearest/<str:h_long>/<str:h_lat>/",views.nearest,name="nearest-hostel"),
    
    
]
