# from rest_framework import permissions

# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user


from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        # for transaction, check through wallet owner
        if hasattr(obj, "wallet"):
            return obj.wallet.user == request.user
        return False
