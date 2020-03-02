from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #     if request.user == obj:
        #         print("True")
        #     return True
        print(obj.filter(user_ins=request.user.is_admin))
        # if (request.user != 'AnonymousUser'):
        #     return obj.email == request.user
        # else:
        #     return False
        return True
