from django.contrib.auth.models import User, Group
from django.http import Http404
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .models import MenuItem, Category,Cart, Order, OrderItem
from .seralizers import CartSerializer, CategorySerializer, MenuItemSerializer, UserSerializer
from .permissions import IsAdminOrManager

#Menu item views
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request):
        
        if request.user.groups.filter(name = 'Manager').exists() or request.user.is_superuser:
            serializedItem = MenuItemSerializer(data = request.data)
            serializedItem.is_valid(raise_exception=True)
            serializedItem.save()
            return Response(serializedItem.data, status = status.HTTP_201_CREATED)
        else:
            return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset= MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def put(self, request, pk):
        if request.user.groups.filter(name = 'Manager').exists():
            try:
                menu_item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MenuItemSerializer(menu_item, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
    def patch(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            try:
                menu_item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
    def delete(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            try:
                menu_item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
            
            menu_item.delete()
            return Response({"message": "Menu item deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        
#User Group Management
class ManagerUsersView(APIView):
    permission_classes = [IsAdminOrManager]
    
    def get_manager_group(self):
        return Group.objects.get(name='Manager')
    
    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except:
            raise Http404("User not found")


    def get(self, request):
        try:
            manager_group = self.get_manager_group()
            manager_users = manager_group.user_set.all()
            serializer = UserSerializer(manager_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied()

        pk = request.data.get('user_id')
        if pk:
            try:
                user = self.get_user(pk)
                manager_group = self.get_manager_group()
                user.groups.add(manager_group)
                return Response({"message": "User granted manager status."}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied:
                return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Please provide a user_id in the request payload."}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        
        if pk:
            try:

                user = self.get_user(pk)
                manager_group = self.get_manager_group()
                
                if manager_group not in user.groups.all():
                    return Response({"message": "User is not a manager."}, status=status.HTTP_400_BAD_REQUEST)
                
                user.groups.remove(manager_group)
                return Response({"message": "User's manager status revoked."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied:
                return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Please provide a user_id in the request payload."}, status=status.HTTP_400_BAD_REQUEST)
