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
    
    def get(self, request, *args):
        try:
            manager_group = Group.objects.get(name='Manager')
            manager_users = manager_group.user_set.all()
            serializer = UserSerializer(manager_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request, *args):

        pk = request.data.get('user_id')
        if pk:
            try:
                user = User.objects.get(pk=pk)
                manager_group = Group.objects.get(name='Manager')
                user.groups.add(manager_group)
                return Response({"message": "User granted manager status."}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied:
                return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Please provide a user_id in the request payload."}, status=status.HTTP_400_BAD_REQUEST)
    
class ManagerRevokeView(APIView):
    permission_classes = [IsAdminOrManager]
    
    def delete(self, request, pk):
        
        if pk:
            try:
                user = User.objects.get(pk=pk)
                manager_group = Group.objects.get(name='Manager')
                
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
        
class DeliveryCrewUsersView(APIView):
    permission_classes = [IsAdminOrManager]
    
    def get(self, request, *args):
        try:
            delivery_group = Group.objects.get(name='DeliveryCrew')
            delivery_crew_users = delivery_group.user_set.all()
            serializer = UserSerializer(delivery_crew_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args):

        pk = request.data.get('user_id')
        if pk:
            try:
                user = User.objects.get(pk=pk)
                delivery_crew_group = Group.objects.get(name='DeliveryCrew')
                user.groups.add(delivery_crew_group)
                return Response({"message": "User granted Delivery Crew status."}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied:
                return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Please provide a user_id in the request payload."}, status=status.HTTP_400_BAD_REQUEST)
        
class DeliveryCrewRevokeView(APIView):
    permission_classes = [IsAdminOrManager]

    def delete(self, request, pk):
        
        if pk:
            try:
                user = User.objects.get(pk=pk)
                delivery_crew_group = Group.objects.get(name='DeliveryCrew')
                
                if delivery_crew_group not in user.groups.all():
                    return Response({"message": "User is not a delivery crew staff."}, status=status.HTTP_400_BAD_REQUEST)
                
                user.groups.remove(delivery_crew_group)
                return Response({"message": "User's delivery crew status revoked."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied:
                return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Please provide a user_id in the request payload."}, status=status.HTTP_400_BAD_REQUEST)
        
#Cart Management view
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            cartItems = Cart.objects.filter(user=user)
            serializer = CartSerializer(cartItems, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
        
        
    
    def post(self, request):
        serializer = CartSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()  # This will call CartSerializer's create method
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            user = request.user
            cart_items = Cart.objects.filter(user=user)
            cart_items.delete()
            return Response({"message": "Cart items deleted successfully."}, status=status. HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
