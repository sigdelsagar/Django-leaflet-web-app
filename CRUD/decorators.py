from django.core.exceptions import PermissionDenied

def user_is_admin_required(function):
    def wrap(request,*args,**kwargs):
    	if request.user.is_anonymous:
    		raise PermissionDenied
    	elif request.user.is_admin:
    		return function(request,*args,**kwargs)
    	else:
    		raise PermissionDenied




        # if request.user.is_admin:
        #     return function(request, *args, **kwargs)
        # elif request.user.is_anonymous:
        # 	raise PermissionDenied
        # else:
        #     raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap 