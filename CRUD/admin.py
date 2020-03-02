from django.utils.html import format_html
from .models import Hostel_info, Hostel_comment, Hostel_Request, Request_Image, Image
from Student.models import PassRate,LikeRate
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.urls import path, reverse
import csv
from django.contrib import admin
from django.contrib import *
from django.contrib.admin.sites import AdminSite
from django.views.decorators.cache import never_cache
from django.core import serializers   

from django.contrib.auth import get_user_model

User = get_user_model()

class HostelInline(admin.TabularInline):
    model = Hostel_comment
    extra = 1


class Custom_Request(admin.ModelAdmin):
    # change_list_template = 'admin/CRUD/Hostel_Request/change_form.html'
    list_display = (
        'Hostel_name',
        'Hostel_Price',
        'Actions',
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('accept/<int:pk>', self.set_accept, name='hostel-accept'),
            path('reject/<int:pk>', self.set_reject, name='hostel-reject'),

        ]
        return my_urls + urls

    def newview(self, obj):
        return True

    def Actions(self, obj):
        return format_html(
            '<a class="btn btn-success btn-sm text-nowrap" href="{}">Accept</a>&nbsp;'
            '<a class="button" href="{}">Reject</a>',
            reverse('admin:hostel-accept', args=[obj.pk]),
            reverse('admin:hostel-reject', args=[obj.pk]),
        )
    #     # TODO: Render action buttons

    def set_accept(self, request, pk):
        # self.model.objects.all().update(is_immortal=True)
        #self.message_user(request, "All heroes are now immortal")
        pre = Hostel_Request.objects.get(pk=pk)
        instance = Hostel_info.objects.create(user_ins=pre.user_ins, Hostel_name=pre.Hostel_name,
                                              Hostel_Address=pre.Hostel_Address, Hostel_Ph_No=pre.Hostel_Ph_No,
                                              Hostel_Mobile_No=pre.Hostel_Mobile_No, Hostel_Price=pre.Hostel_Price,
                                              Hostel_Estd=pre.Hostel_Estd,  about=pre.about,
                                              Hostel_long=pre.Hostel_long, Hostel_lat=pre.Hostel_lat)
        print(instance)
        self.message_user(request, "moved to main hostel")
        pre_img = pre.request_image_set.all()
        for e in pre_img:
            Image.objects.create(Hostel_image=instance, image=e.image)

        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        # print(previous.Hostel_Price)
        # # saccepted.save()
        return HttpResponseRedirect("../")

    def set_reject(self, request, pk):
        # self.model.objects.all().update(is_immortal=True)
        self.message_user(request, "All heroes are now mortal")
        Del = Hostel_Request.objects.get(pk=pk)
        Del.delete()
        return HttpResponseRedirect("../")


class Custom_Image(admin.ModelAdmin):
    list_display = ('image', 'hostel', 'edit')

    def hostel(self, obj):
        return obj.Hostel_image

    def edit(self, obj):
        return format_html('<a class="button" href="#">edit</a>&nbsp;')

    edit.short_description = ''


class CustomAdminSite(admin.AdminSite):

    @never_cache
    def index(self, request, extra_context=None):
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        queryset = PassRate.objects.all().values('pass_year','student_no','Hostel__Hostel_name').order_by('pass_year')
        queryset2 = LikeRate.objects.all().values('likes','Hostel__Hostel_name').order_by('likes')
        bargraph = self.LikeCount(queryset2)
        print(bargraph)
        extra_content={}
        colour=[]
        label=[]
        for i,each in enumerate(queryset):
            label.append(each['pass_year'])
            if (each['Hostel__Hostel_name'] in extra_content.keys()):
                if ('data' in extra_content[each['Hostel__Hostel_name']].keys()):
                    extra_content[each['Hostel__Hostel_name']]['data'].append(each['student_no'])            
            else:
                extra_content[each['Hostel__Hostel_name']]={"label":each['Hostel__Hostel_name'],"data":[each['student_no']]}
        pass_data= json.dumps(dict(extra_content), cls=DjangoJSONEncoder)
        pass_rate=json.loads(pass_data)
        print(type(pass_rate))
        labels=list(set(label))
        labels.sort()
        bargrap=json.dumps(dict(bargraph), cls=DjangoJSONEncoder)
        # bargraphs=json.loads(bargrap)
        return super().index(request,extra_context={"pass_rate":pass_rate,"labels":labels,"bargrap":bargrap})

    def LikeCount(self,queryset):
        extra_content={}
        label=[]
        data=[]
        for i,each in enumerate(queryset):
            label.append(each["Hostel__Hostel_name"])
            data.append(each["likes"])
        extra_content["labels"]=label
        extra_content["data"]=data
        return extra_content
        

        
    

    def maleFemaleHostel(self, request, extra_context=None):
        gender = request.GET["gender"]    
        context={"json":  serializers.serialize(
            "json", Hostel_info.objects.filter(Hostel_type=gender))}
        return JsonResponse(context)

    def get_urls(self):
        from django.urls import path
        urls = super(CustomAdminSite, self).get_urls()
        custom_urls = [
            path('desired/',
                 self.admin_view(self.maleFemaleHostel), name="male-Female"),
        ]
        return urls + custom_urls


custom_admin_site = CustomAdminSite()


@admin.register(Hostel_info, site=custom_admin_site)
class Custom_info(admin.ModelAdmin):
    list_display = ('Hostel_name', 'Hostel_Address',
                    'Hostel_price', 'Category')
    inlines = [HostelInline]

    def Hostel_price(self, obj):
        return obj.Hostel_Price

    Hostel_price.short_description = '(Rs)Price'

    def Category(sef, obj):
        if (obj.Hostel_type == 'male'):
            return format_html('<i class="fa fa-mars" style="color:blue"></i>')
        elif (obj.Hostel_type == 'female'):
            return format_html('<i class="fa fa-venus"  style="color:#E75480"></i>')

class Custom_Token(admin.ModelAdmin):
    # change_list_template = 'admin/CRUD/Hostel_Request/change_form.html'
    list_display = (
        'key',
        'user',
        'created',
    )





AdminSite.site_header = "Hostel Admin"
AdminSite.site_title = "Hostel aaaaaAdmin"
AdminSite.index_title = "Welcome to Hostel Admin Portal"

from rest_framework.authtoken.models import Token
# admin.site.register(Hostel_info, Custom_info)
custom_admin_site.register(Hostel_Request, Custom_Request)
custom_admin_site.register(Request_Image)
custom_admin_site.register(Image, Custom_Image)
custom_admin_site.register(Hostel_comment)
custom_admin_site.register(Token,Custom_Token)
custom_admin_site.register(User)