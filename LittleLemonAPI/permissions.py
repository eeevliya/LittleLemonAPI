from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Manager').exists()
    
class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        if request.user and request.user.groups.filter(name='Manager').exists():
            return True
        
        return False