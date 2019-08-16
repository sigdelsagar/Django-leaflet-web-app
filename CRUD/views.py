from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from .models import Hostel_info,Hostel_Request,Request_Image,Image
from .forms import Hostel_Request_Form, Hostel_comment
from django.db.models import Q
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from .serializers import Hostel_infoSerializers, Hostel_commentSerializers,ImageSerializers

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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

def index(request):
    return render(request,"CRUD/index.html")

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/hostel/login/")


class LoginView(FormView):
    template_name = "CRUD/login.html"
    form_class = LoginForm
    redirect_field_name = "/hostel/client-map/" 
    success_url="/hostel/client-map/"          #-------sends to client if not admin

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        pword = form.cleaned_data["password"]
        user = authenticate(email=email, password=pword)
        if user is not None:
            login(self.request, user)
            if user.is_admin:
                return redirect("/hostel/main/")
        else:
            return render(self.request, "CRUD/login.html", {"error": "Invalid Credential", "form": form})
        return super().form_valid(form)

class ClientLoginView(FormView):
    template_name = "CRUD/login.html"
    form_class = LoginForm
    success_url = "/hostel/client/"
    
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
    success_url = "/hostel/activation-sent/"

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
        message = 'Please use this link to login http://'+str(current_site)+'/hostel/activate/'+str(uid)+'/'+str(token)+'/'
                    
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
        return HttpResponseRedirect('/hostel/client/')
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


class Hostel_CreateView(LoginRequiredMixin,UserPassesTestMixin,FormView, SuccessMessageMixin):
    login_url = "/hostel/login/"
    form_class = Hostel_Request_Form

    template_name = "main.html"
    success_url = "/hostel/view/"
    context_object_name = 'form'  # default is object_list
    # def form_valid(self,form):
    #     Hostel_name = form.cleaned_data["Hostel_name"]
    #     Hostel_Address=form.cleaned_data['Hostel_Address']

      
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    

class Comments(LoginRequiredMixin,UserPassesTestMixin,ListView):
    login_url = "/hostel/login/"
    model = Hostel_comment 
    template_name = "CRUD/comments.html"
    fields='__all__'
    success_url = "/hostel/comments/"
    context_object_name = 'form'  # default is object_list
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False       
    
class Hostel_Comments:
    @login_required(login_url='/hostel/login/')
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
    login_url="/hostel/login/"
    form_class = Hostel_Request_Form
    template_name = "CRUD/ClientHome.html"
    success_url = "/hostel/client/"
    context_object_name = 'form'  # default is object_list
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES or None)
        files = request.FILES.getlist('image')
        if form.is_valid():
            instance = form.save(commit=False)           
            instance.user_ins = request.user
            lat=request.POST['Hostel_lat']
            lon=request.POST['Hostel_long']
            instance.Hostel_long = lon
            instance.Hostel_lat = lat           
            form.save()
            for f in files:
                try:
                    img=Request_Image.objects.create(Hostel_image=instance,image=f)
                    img.save()
                except:
                    break        
            return HttpResponseRedirect('/hostel/client/')
        return render(request, self.template_name, {'form': form})
    
# def form_valid(self, form):
#         instance=form.save(commit=False)
#         longi=request.POST.get('Hostel_long')
#         lat=request.POST.get('Hostel_lat')
#         print(longi)
#         print(lat)
#         instance.user_ins(self.request.user)
#         instance.Hostel_long(longi)
#         instance.Hostel_lat(lat)
#         instance.save()
#         return super(Hostel_CreateView, self).form_valid(form)

class Hostel_AcceptView:
    
    @user_is_admin_required
    def accept(self, pk):
        pre = Hostel_Request.objects.get(pk=pk)
        instance=Hostel_info.objects.create(user_ins=pre.user_ins, Hostel_name=pre.Hostel_name,
                                    Hostel_Address=pre.Hostel_Address, Hostel_Ph_No=pre.Hostel_Ph_No,
                                    Hostel_Mobile_No=pre.Hostel_Mobile_No, Hostel_Price=pre.Hostel_Price,
                                    Hostel_Estd=pre.Hostel_Estd,Hostel_type=pre.Hostel_type,
                                    Hostel_long=pre.Hostel_long, Hostel_lat=pre.Hostel_lat,
                                    wifi=pre.wifi, lodging=pre.lodging,
                                    studyRoom=pre.studyRoom, medicalFacility=pre.medicalFacility,
                                    singleRoom=pre.singleRoom, dormitory=pre.dormitory,
                                     laundary=pre.laundary,about=pre.about,)            
        pre_img=pre.request_image_set.all()
        for e in pre_img:
            Image.objects.create(Hostel_image=instance,image=e.image)
        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        return HttpResponseRedirect("/hostel/hostel-request-list/")
    @user_is_admin_required
    def requestdetail(self,pk):
        
        form = Hostel_Request.objects.filter(pk=pk)
        
        return render(request,"CRUD/view-request-hostel.html",{'form':form})

# class Hostel_DetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
#     login_url='/login/'
#     template_name='CRUD/view-request-hostel.html'
#     model=Hostel_Request
#     pk_url_kwarg = 'pk'
#     context_object_name='form'
#     def test_func(self):                                #fail test only work if returned false
#         if self.request.user.is_admin:
#             return self.request.user
#         return False

def hostel_DetailView(request,pk):
    form=Hostel_Request.objects.get(pk=pk)
    image=Request_Image.objects.filter(Hostel_image=form)
    return render(request,'CRUD/view-request-hostel.html',{'form':form,'image':image})

        
class Hostel_RejectView(LoginRequiredMixin,UserPassesTestMixin,SuccessMessageMixin):
    success_message="Deleted successfully"
    login_url = "/hostel/login/"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    
    def reject(self, pk):       
        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        return HttpResponseRedirect("/hostel/hostel-request-list/")

class Hostels(LoginRequiredMixin, UserPassesTestMixin,ListView):
    login_url = "/hostel/login/"
    model = Hostel_info
    context_object_name = 'form'
    template_name = "CRUD/hostel_list.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
    

class Hostel_ListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url = "/hostel/login/"
    model = Hostel_info
    context_object_name = 'form'
    template_name = "CRUD/hostel.html"
    redirect_field_name='/hostel/login/'
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
    login_url = "/hostel/login/"
    model = Hostel_Request
    context_object_name = 'form'
    template_name = "CRUD/hostel_req_tab.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   

class Users_ListView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url = "/hostel/login/"
    model = User
    context_object_name = 'form'
    template_name = "CRUD/users.html"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   
    
class Hostel_DeleteView(LoginRequiredMixin,SuccessMessageMixin,UserPassesTestMixin,DeleteView):
    login_url = "/hostel/login/"   
    model = Hostel_info
    pk_url_kwarg = 'id'
    template_name = "CRUD/hostel_list.html"
    success_message = "Deleted successfully"
    success_url = "/hostel/hostel-list/"
    def test_func(self):                                #fail test only work if returned false
        if self.request.user.is_admin:
            return self.request.user
        return False   
   
    def delete(self, request, *args, **kwargs):         #message after deleting
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(Hostel_DeleteView, self).delete(request, *args, **kwargs)
    
    
class Hostel_UpdateView(SuccessMessageMixin,UserPassesTestMixin, UpdateView):
    model = Hostel_info
    fields = '__all__'
    pk_url_kwarg = 'id'
    template_name = "CRUD/edit_hostel.html"
    success_message = "Edited successfully"
    success_url = "/hostel/hostel-list/"
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

    @login_required(login_url='/hostel/login/')
    def deleteComment(request):
        usr=User.objects.get(email=request.user)
        pre=usr.hostel_info_set.all()
        for e in pre:
            for h in e.hostel_comment_set.all():     
                h.delete()
        return HttpResponseRedirect("/hostel/hostel-comments/")

    @user_is_admin_required
    def deleteCommentAll(request):
        Hostel_comment.objects.all().delete()
        return HttpResponseRedirect("/hostel/comments/")
    

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

@login_required(login_url='/hostel/login/')
def clientmap(request):
    # from django.core import serializers
    #json_data = serializers.serialize("json",None)
     
    return render(request,'CRUD/clientpage.html',{'json':'true'})

@login_required(login_url='/hostel/login/')
def totalhostel(request):
    from django.core import serializers
    h = Hostel_info.objects.all()
    e=Image.objects.all()
    context = {
        'e': e,
        'h':h,
        }
    return render(request, 'CRUD/totalhostel.html', context)  

@login_required(login_url='/hostel/login/')
def direction(request,h_long,h_lat):
    from django.core import serializers
    h_lat=h_lat
    h_long=h_long
    
    
    # print (h_lat)
    #h_long=request.GET.get('h_long')
    print (h_long)
    print (h_lat)    
    return render(request,'CRUD/clientpage.html',{'h_long':h_long,'h_lat':h_lat,'json':'true'})

# @csrf_protect
# def comment(request):
#     from django.core import serializers
#     if request.method == "GET":
#         hostel_id=request.GET['hostel_id']
#         print (hostel_id)     
#         h=Hostel_info.objects.get(id=hostel_id)  
#         nonjson=Hostel_comment.objects.filter(commenton=h).order_by('-id')     
#         json_data = serializers.serialize("json",nonjson)
#         data={
#         'comments':json_data,
#         #'nonjson':nonjson
#         }
#         return JsonResponse(data)
#     if request.method == "POST":
        
#         comment=request.POST['hostel_comment']
#         commenton=request.POST['hostel_id']
#         email=request.POST['email']
#         instance=Hostel_info.objects.get(id=commenton)
#         post_comment=Hostel_comment.objects.create(comment=comment,commenton=instance,email=email)
#         json_data = serializers.serialize("json",Hostel_comment.objects.filter(commenton=instance).order_by('-id'))
#         data={
#         'comments':json_data,
#         }
#         return JsonResponse(data)
#     return render(request,'CRUD/totalhostel.html',{'form':form}) 
@login_required(login_url='/hostel/login/')
def commentform(request,id):
    if request.method == "POST":       
        comment=request.POST.get('areaforinfo')
        print (comment)
        commenton=id
        
        instance=Hostel_info.objects.get(id=commenton)
        post_comment=Hostel_comment.objects.create(comment=comment,commenton=instance,email=request.user)
        image=Image.objects.filter(Hostel_image=instance)
        hostel_comment=Hostel_comment.objects.filter(commenton=instance).order_by('-id')
    else:
        instance=Hostel_info.objects.get(id=id)
        image=Image.objects.filter(Hostel_image=instance)
        hostel_comment=Hostel_comment.objects.filter(commenton=instance).order_by('-id')
        return render(request,'CRUD/commentform.html',{'comment':hostel_comment,'h':instance,'e':image})
    return render(request,'CRUD/commentform.html',{"ins":instance,'e':image,'comment':hostel_comment,
        'h':instance})




@login_required(login_url='/hostel/login/')
def cheapSortHostel(request):
    import collections
    def partition(arr,low,high): 

        i = ( low-1 )         # index of smaller element 
        pivot = arr[high]     # pivot 
        for j in range(low , high): 
            if   arr[j] <= pivot: 
                i = i+1 
                arr[i],arr[j] = arr[j],arr[i]  
        arr[i+1],arr[high] = arr[high],arr[i+1] 
        return ( i+1 ) 
  
    def quickSort(arr,low,high): 
        if low < high:   
            pi = partition(arr,low,high)   
            quickSort(arr, low, pi-1) 
            quickSort(arr, pi+1, high)  

    obj=Hostel_info.objects.all()
    e=Image.objects.all()
    price=[]
    for each in obj:
        if each.Hostel_Price!=None:
            price.append(each.Hostel_Price)
            print(each.Hostel_Price)
    
    
    quickSort(price,0,(len(price)-1))
    h_obj=[]
    
    def Remove(duplicate):         
        final_list = [] 
        for num in duplicate: 
            if num not in final_list: 
                final_list.append(num) 
        return final_list       
    nonrepeat=Remove(price)                                #removes duplicate
    print("repeat",nonrepeat)
    for each in nonrepeat:
        for h in Hostel_info.objects.filter(Hostel_Price=each):
            print(h)      
            h_obj.append(h)


    return render(request,'CRUD/totalhostel.html',{'h':h_obj,'e':e})

@login_required(login_url='/hostel/login/')
def expenSortHostel(request):
    import collections
    def partition(arr,low,high): 

        i = ( low-1 )         # index of smaller element 
        pivot = arr[high]     # pivot 
        for j in range(low , high): 
            if   arr[j] >= pivot: 
                i = i+1 
                arr[i],arr[j] = arr[j],arr[i]  
        arr[i+1],arr[high] = arr[high],arr[i+1] 
        return ( i+1 ) 
  
    def quickSort(arr,low,high): 
        if low < high:   
            pi = partition(arr,low,high)   
            quickSort(arr, low, pi-1) 
            quickSort(arr, pi+1, high)  



    obj=Hostel_info.objects.all()
    e=Image.objects.all()
    price=[]
    for each in obj:
        
        if each.Hostel_Price!=None:
            price.append(each.Hostel_Price)
            print(each.Hostel_Price)
    
    quickSort(price,0,(len(price)-1))
    h_obj=[]
    def Remove(duplicate):         
        final_list = [] 
        for num in duplicate: 
            if num not in final_list: 
                final_list.append(num) 
        return final_list       
    nonrepeat=Remove(price)                                #removes duplicate
    print("repeat",nonrepeat)
    for each in nonrepeat:
        for h in Hostel_info.objects.filter(Hostel_Price=each):
            print(h)      
            h_obj.append(h)


    return render(request,'CRUD/totalhostel.html',{'h':h_obj,'e':e})

@login_required(login_url='/hostel/login/')
def sortMale(request):
    obj=Hostel_info.objects.filter(Hostel_type='male')
    e=Image.objects.all()
    return render(request,'CRUD/totalhostel.html',{'h':obj,'e':e})

@login_required(login_url='/hostel/login/')
def sortFemale(request):
    obj=Hostel_info.objects.filter(Hostel_type="female")
    print(obj)
    e=Image.objects.all()
    return render(request,'CRUD/totalhostel.html',{'h':obj,'e':e})

@login_required(login_url='/hostel/login/')
def nearest(request,h_long,h_lat):
    print(h_long,h_lat)
    h=Hostel_info.objects.all()
    shortest={}
    long_lat={}
    h_long=float(h_long)
    h_lat=float(h_long)
   
    innerlist=[]
    tupple=()
    finallist=[]
    def calc(h_long,h_lat,longi,lati):
        from math import sin, cos, sqrt, atan2, radians
        dlon = float(h_long) - float(longi)       
        dlat = float(h_lat) - float(lati)
        a = sin(dlat / 2)**2 + cos(float(lati)) * cos(float(h_lat)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        R = 6373.0
        distance = R * c      
        return distance
    index={}
    k=1
    for each in h:       
        innerlist.append(each.Hostel_long)       
        innerlist.append(each.Hostel_lat)       
        tupple=tuple(innerlist)
        finallist.append(tupple)
        innerlist.remove(each.Hostel_long)
        innerlist.remove(each.Hostel_lat)
        index.update({''+str(each.id):tupple})
        k=k+1
    i=1
    
    for each in finallist:
        
        long_lat.update({'hostel'+str(i):each})
        i=i+1
    j=1


    import operator
    for state,value in index.items():
        dummy=[]
       
        for each in value:
            dummy.append(each)
            last_long=each
        longi=dummy[0]
        lati=dummy[1]
        short=calc(h_long,h_lat,longi,lati)
        print ("short",short)
        print("stat",state)
        shortest.update({''+str(state):short})
        j=j+1
    print (shortest)
    print("min",sorted(shortest.items(), key=lambda x: x[1]))
    
    print(min(shortest, key=lambda k: shortest[k]))

    # less=[]
    # for state,value in shortest.items():
    #         less.append(value)
    # print()
    # #nearestvalue=min(shortest)
    print (min(shortest))
    print (near)

    nearesthostel=shortest.get(near)
    from django.core import serializers
    match=Hostel_info.objects.filter(id=near)
    #print (match)
    json_data = serializers.serialize("json",match)
    return render(request,'CRUD/clientpage.html',{'json':json_data})


    



        

    

@login_required(login_url='/hostel/login/')
def searchhostel(request):                          #in map
    from django.core import serializers
    try:
        search=request.GET['name']
    except:
        return render(request,'CRUD/clientpage.html',{'json':'true'})    
    if (search!=None):
        if (search=='all hostel' or search=='Hostels'):
            print('true')
            match=Hostel_info.objects.all()
            json_data = serializers.serialize("json",match)
            return render(request,'CRUD/clientpage.html',{'json':json_data})
        match = Hostel_info.objects.filter(Q(Hostel_name__icontains=search))
        print (match)
        json_data = serializers.serialize("json",match)
        print (json_data)
    return render(request,'CRUD/clientpage.html',{'json':json_data})

class Api_Hostel(generics.ListAPIView):
    queryset = Hostel_info.objects.all()
    serializer_class = Hostel_infoSerializers

class Api_Hostel_Add(generics.CreateAPIView):
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

class Api_Image(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializers

