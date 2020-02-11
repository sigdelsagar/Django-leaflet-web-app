from django.contrib import admin
from CRUD.admin import custom_admin_site, CustomAdminSite
from .models import PassRate, LikeRate


class Custom_Student(admin.ModelAdmin):
    list_display = ('Hostel_name', 'pass_year', 'student_no')

    def Hostel_name(self, obj):
        return (obj.Hostel)

    Hostel_name.short_description = 'Hostel'


class Custom_Like(admin.ModelAdmin):
    list_display = ('Hostel_name', 'likes')

    def Hostel_name(self, obj):
        return (obj.Hostel)


custom_admin_site.register(LikeRate, Custom_Like)

custom_admin_site.register(PassRate, Custom_Student)
