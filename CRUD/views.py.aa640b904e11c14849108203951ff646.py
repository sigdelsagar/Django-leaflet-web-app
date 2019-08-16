from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from .models import Hostel_info,Hostel_Request,Request_Image
from .forms import Hostel_Request_Form, Hostel_comment
from django.db.models import Q
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from .serializers import Hostel_infoSerializers, Hostel_commentSerializers

from django.contrib.auth.decorators import *
from django.contrib.admin.views.decorators import *
from CRUD.decorators import user_is_admin_required

from django.contrib.auth import get_user_model

from django.views.generic import ListView, DetailView, TemplateView, FormView, View, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .forms import *
from django.contrib.auth import authenticate, login, logout
#send mail
from django.core.mail import send_mail

#Encrypion,decryption,text byte and text
from django.conf import settings
from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from CRUD.token import account_activation_token
from django.contrib.sites.shortcuts import get_current_site


User = get_user_model()


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/login/")


class LoginView(FormView):
    template_name = "CRUD/login.html"
    form_class = LoginForm
    success_url = "/client/"

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        pword = form.cleaned_data["password"]
        user = authenticate(email=email, password=pword)
        if user is not None:
            login(self.request, user)
            if user.is_admin:
                return redirect("/main/")
        else:
            return render(self.request, "CRUD/login.html", {"error": "Invalid Credential", "form": form})
        return super().form_valid(form)

class ClientLoginView(FormView):
    template_name = "CRUD/login.html"
    form_class = LoginForm
    success_url = "/client/"
    
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        pword = form.cleaned_data["password"]
        user = authenticate(email=email, password=pword)
        if user is not None:
            login(self.request, user)            
        else:
            return render(self.request, "CRUD/login.html", {"error": "Invalid Credential", "form": form})
        return super(ClientLoginView,self).form_valid(form)

      

class ClientRegisterView(FormView):
    template_name = "CRUD/RegistrationForm.html"
    form_class = SignupForm
    success_url = "/activation-sent/"

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        pword = form.cleaned_data["password"]
        #send message and token for authentication
        subject = 'Thank you for registering to our site'    
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]
        current_site = get_current_site(self.request).domain
        
        instance=User.objects.create_user(email=email, password=pword, is_customer=True,is_active=False)
        uid = urlsafe_base64_encode(force_bytes(instance.pk)).decode()
        token = account_activation_token.make_token(instance)
        message = 'Please use this link to login http://'+str(current_site)+'/activate/'+str(uid)+'/'+str(token)+'/'
                    
        send_mail(subject, message, email_from, recipient_list)                    
        return super().form_valid(form)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()        
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.active = True
        user.save()
        login(request, user)
        return HttpResponseRedirect('/client/')
    else:
        return render(request, 'CRUD/code_verification.html',{'error':'Token is expired'})


def verifyNotification(request):
    return render(request,"CRUD/code_verification.html",{'message1':'Activate Account','message2':'Please confirm your email address to complete registration'})


# class RegisterView(FormView):
#     template_name = "CRUD/RegistrationForm.html"
#     form_class = SignupForm
#     success_url = "/client-login/"

#     def form_valid(self, form):
#         email = form.cleaned_data["email"]
#         pword = form.cleaned_data["password"]
#         User.objects.create_user(email=email, password=pword)
#         return super().form_valid(form)


class Hostel_CreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView, SuccessMessageMixin):
    login_url = "/login/"
    form_class = Hostel_Request_Form
    template_name = "main.html"
    success_url = "/view/"
    context_object_name = 'form'  # default is object_list
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    

class Comments(LoginRequiredMixin,UserPassesTestMixin,ListView):
    login_url = "/login/"
    model = Hostel_comment 
    template_name = "CRUD/comments.html"
    fields='__all__'
    success_url = "/comments/"
    context_object_name = 'form'  # default is object_list
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False       
    
class Hostel_Comments:
    @login_required(login_url='/login/')
    def get(request):
        usr=User.objects.get(email=request.user)
        pre=usr.hostel_info_set.all()
        lst=[]
        for e in pre:
            for h in e.hostel_comment_set.all():     
                lst.append(h)
        context={'form':lst,'pre':pre}
        return render(request,'CRUD/ClientHostelComments.html',context)


class Client_CreateView(LoginRequiredMixin,SuccessMessageMixin, FormView,CreateView ):
    login_url="/login/"
    form_class = Hostel_Request_Form
    template_name = "CRUD/ClientHome.html"
    success_url = "/client/"
    context_object_name = 'form'  # default is object_list
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES or None)
        files = request.FILES.getlist('image')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user_ins = request.user
            form.save()
            for f in files:
                try:
                    img=Request_Image.objects.create(Hostel_image=instance,image=f)
                    img.save()
                except:
                    break        
            return HttpResponseRedirect('/client/')
        return render(request, self.template_name, {'form': form})
    
class Hostel_AcceptView:
    
    @user_is_admin_required
    def accept(self, pk):
        pre = Hostel_Request.objects.get(pk=pk)
        instance=Hostel_info.objects.create(user_ins=pre.user_ins, Hostel_name=pre.Hostel_name,
                                    Hostel_Address=pre.Hostel_Address, Hostel_Ph_No=pre.Hostel_Ph_No,
                                    Hostel_Mobile_No=pre.Hostel_Mobile_No, Hostel_Price=pre.Hostel_Price,
                                    Hostel_Estd=pre.Hostel_Estd,
                                    Hostel_long=pre.Hostel_long, Hostel_lat=pre.Hostel_lat)            
        pre_img=pre.request_image_set.all()
        for e in pre_img:
            Image.objects.create(Hostel_image=instance,image=e.image)
        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        return HttpResponseRedirect("/hostel-request-list/")
    @user_is_admin_required
    def requestdetail(self,pk):
        print ("somethin")
        form = Hostel_Request.objects.filter(pk=pk)
        print("nothin")
        return render(request,"CRUD/view-request-hostel.html",{'form':form})

class Hostel_DetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
    login_url='/login/'
    template_name='CRUD/view-request-hostel.html'
    model=Hostel_Request
    pk_url_kwarg = 'pk'
    context_object_name='form'
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False
        
class Hostel_RejectView(LoginRequiredMixin,UserPassesTestMixin,SuccessMessageMixin):
    success_message="Deleted successfully"
    login_url = "/login/"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    
    def reject(self, pk):       
        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        return HttpResponseRedirect("/hostel-request-list/")

class Hostels(LoginRequiredMixin, UserPassesTestMixin,ListView):
    login_url = "/login/"
    model = Hostel_info
    context_object_name = 'form'
    template_name = "CRUD/hostel_list.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    

class Hostel_ListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url = "/login/"
    model = Hostel_info
    context_object_name = 'form'
    template_name = "CRUD/hostel.html"
    redirect_field_name='/login/'
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
        
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args,**kwargs)
        context['hostel_req'] = Hostel_Request.objects.count()
        context['hostel_obj'] = Hostel_info.objects.all()        
        return context

class Hostel_Request_ListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url = "/login/"
    model = Hostel_Request
    context_object_name = 'form'
    template_name = "CRUD/hostel_req_tab.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   

class Users_ListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url = "/login/"
    model = User
    context_object_name = 'form'
    template_name = "CRUD/users.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   
    
class Hostel_DeleteView(SuccessMessageMixin,UserPassesTestMixin,DeleteView):
    model = Hostel_info
    pk_url_kwarg = 'id'
    template_name = "CRUD/hostel_list.html"
    success_message = "Deleted successfully"
    success_url = "/hostel-list/"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(Hostel_DeleteView, self).delete(request, *args, **kwargs)
    
    
class Hostel_UpdateView(SuccessMessageMixin,UserPassesTestMixin, UpdateView):
    model = Hostel_info
    fields = '__all__'
    pk_url_kwarg = 'id'
    template_name = "CRUD/edit_hostel.html"
    success_message = "Edited successfully"
    success_url = "/hostel-list/"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False

    def get_context_data(self,*args,**kwargs):
        context=super(Hostel_UpdateView,self).get_context_data(*args,**kwargs)
        pre = Hostel_info.objects.get(id=self.kwargs['id'])
        context['img']=pre.image_set.all()
        context['del']=self.kwargs['id']
        return context


# def show_info(request):
#     allinfo = Hostel_info.objects.all()
#     context = {'allinfo': allinfo}
#     return render(request, 'CRUD/view_table.html', context)


# def Edit(request, id):
#    # previous = Hostel_info.objects.get(pk=id)
#     previous = get_object_or_404(Hostel_info, id=id)
#     if request.method == 'POST':
#         form = Hostel_Request_Form(request.POST or None, request.FILES, instance=previous)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Data is edited ")
#             return redirect('CRUD:home')
#     else:
#         form = Hostel_Request_Form(instance=previous)
#     return render(request, 'CRUD/home.html', {'form': form})
#
#
class DeleteGroup:
    @user_is_admin_required
    def deleteHostel(request):
        if request.method == 'POST':
            dele =request.POST.getlist('acs') 
            if dele:
                try:
                    for i in dele:
                        Hostel_info.objects.filter(id=i).delete()
                    messages.success(request, "Deleted successfully")
                    return redirect('CRUD:hostel-list')
            
                except:
                    messages.success(request, "Could not deleted")                    
            else:
                messages.warning(request, "Select hostel to delete")
                return redirect('CRUD:hostel-list')

    @user_is_admin_required        
    def deleteUser(request):
        if request.method == 'POST':
            dele =request.POST.getlist('acs') 
            print(dele)
            if dele:
                try:
                    for i in dele:
                        User.objects.filter(id=i).delete()
                    messages.success(request, "Deleted successfully")
                    return redirect('CRUD:list-users')
                except:
                    messages.success(request, "Couldnot delete")                
            else:
                messages.warning(request, "Select user to delete")
                return redirect('CRUD:list-users')

    @login_required(login_url='/login/')
    def deleteComment(request):
        usr=User.objects.get(email=request.user)
        pre=usr.hostel_info_set.all()
        for e in pre:
            for h in e.hostel_comment_set.all():     
                h.delete()
        return HttpResponseRedirect("/hostel-comments/")

    @user_is_admin_required
    def deleteCommentAll(request):
        Hostel_comment.objects.all().delete()
        return HttpResponseRedirect("/comments/")
    

#
# def home(request):
#     if request.method == 'POST':
#         form = Hostel_Request_Form(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Saved successfully")
#             return redirect('CRUD:home')
#     else:
#         form = Hostel_Request_Form()
#     args = {'form': form}
#     return render(request, 'CRUD/home.html', args)

#
@user_is_admin_required
def Search(request):
    if request.method == 'POST':
        srch = request.POST.get('srh')
      
        if srch:
            match = Hostel_info.objects.filter(Q(Hostel_name__icontains=srch) |
                                               Q(Hostel_Address__icontains=srch))
            print (match)
            usr = User.objects.filter(Q(email__icontains=srch))
            print(usr)
            if match:
                return render(request, 'CRUD/search.html', {'match': match})
            elif usr:
                return render(request, 'CRUD/search.html', {'usr': usr})
            else:
                messages.error(request, 'No such result found')
        else:
            return redirect('CRUD:search')
    return render(request, 'CRUD/search.html')


# def search(request):
#     if request.method == 'POST':
#         usr = request.POST['u']
#         if usr:
#             match = User.objects.filter(Q(email__icontains=usr))
#             if match:
#                 return render(request, 'CRUD/search.html', {'match': match})
#             else:
#                 messages.error(request, 'No such result found')
#         else:
#             return redirect('CRUD:search')
   

#     return render(request, 'CRUD/search.html')

@user_is_admin_required
def mapview(request):
    from django.core import serializers
    json_data = serializers.serialize("json",Hostel_info.objects.all())
    context = {
        'json': json_data,
        }
    return render(request, 'CRUD/map.html', context)

def clientmap(request):
    from django.core import serializers
    json_data = serializers.serialize("json",Hostel_info.objects.all())
    context = {
        'json': json_data,
        }
    return render(request, 'CRUD/clientpage.html', context)

class Api_Hostel(generics.ListAPIView):
    queryset = Hostel_info.objects.all()
    serializer_class = Hostel_infoSerializers


class Api_Comment(generics.ListAPIView):
    queryset = Hostel_comment.objects.all()
    serializer_class = Hostel_commentSerializers


class Api_Crud(generics.ListAPIView, generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    queryset = Hostel_comment.objects.all()
    lookup_url_kwarg = 'id'
    #lookup_field = 'id'
    serializer_class = Hostel_commentSerializers

    def put(self, request, id=None):
        return self.update(request, id)


