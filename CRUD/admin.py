from django.contrib import admin
from django.contrib import *
import csv
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Hostel_info, Hostel_comment, Hostel_Request,Request_Image,Image
from django.utils.html import format_html
from django.urls import reverse
    

# class CustomerHostel(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         return False


# class Hostel_Comment(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         return False
    


class Custom_Request(admin.ModelAdmin):
    # change_list_template = 'admin/CRUD/Hostel_Request/change_form.html'
    class Meta:
        model = Hostel_info
    list_display = (
        'Hostel_name',
        'Hostel_Price',
        'Actions',
    )
    readonly_fields = ["hostel_image",]
    

    def hostel_image(self, obj):
        return format_html('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.image.url,
            width=obj.image.width,
            height=obj.image.height,
            )
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('accept/<int:pk>', self.set_accept, name='hostel-accept'),
            path('reject/<int:pk>', self.set_reject, name='hostel-reject'),
        ]
        return my_urls + urls
    
    def has_add_permission(self, request):
        return False
    

    def Actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Accept</a>&nbsp;'
            '<a class="button" href="{}">Reject</a>',
            reverse('admin:hostel-accept', args=[obj.pk]),
            reverse('admin:hostel-reject', args=[obj.pk]),
        )
        # TODO: Render action buttons

    def set_accept(self, request, pk):
        # self.model.objects.all().update(is_immortal=True)
        #self.message_user(request, "All heroes are now immortal")
        pre = Hostel_Request.objects.get(pk=pk)
        instance=Hostel_info.objects.create(user_ins=pre.user_ins, Hostel_name=pre.Hostel_name,
                                   Hostel_Address=pre.Hostel_Address, Hostel_Ph_No=pre.Hostel_Ph_No,
                                   Hostel_Mobile_No=pre.Hostel_Mobile_No, Hostel_Price=pre.Hostel_Price,
                                   Hostel_Estd=pre.Hostel_Estd,  Hostel_About=pre.Hostel_About,
                                   Hostel_long=pre.Hostel_long, Hostel_lat=pre.Hostel_lat)
        print(instance)
        self.message_user(request, "moved to main hostel")
        pre_img=pre.request_image_set.all()
        for e in pre_img:
            Image.objects.create(Hostel_image=instance,image=e.image)
        
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


admin.site.register(Hostel_info)
admin.site.register(Hostel_Request, Custom_Request)
admin.site.register(Request_Image)
admin.site.register(Image)
admin.site.register(Hostel_comment)
