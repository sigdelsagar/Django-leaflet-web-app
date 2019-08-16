from CRUD.models import Hostel_info,Hostel_comment
from django.contrib.auth import get_user_model

User = get_user_model()


def global_obj(request):

    
    hostel_total = Hostel_info.objects.count()
    user_total = User.objects.count()
    latestUser = User.objects.all().order_by('-timestamp')[:3]
    comment_total = Hostel_comment.objects.count()
    return {
            'hostel_total': hostel_total,
            'user_total': user_total,           
            'latestUser': latestUser,
            'comment_total':comment_total,
            }
