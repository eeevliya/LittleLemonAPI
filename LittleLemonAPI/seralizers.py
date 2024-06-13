from django.utils.text import slugify
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import bleach
from .models import MenuItem, Category, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    
    def validate(self, attrs):
        
        slugInput = attrs['slug']
        titleInput = attrs['title']
        if(not slugInput or slugInput == ""):
            raise serializers.ValidationError('Slug field cannot be empty')
        if(not titleInput or titleInput == ""):
            raise serializers.ValidationError('Title field cannot be empty')
        titleInput = bleach.clean(titleInput)
        slugInput = slugify(bleach.clean(slugInput))
    
    class Meta:
        model = Category
        fields=['id', 'slug', 'title']
        
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )
    
    def validate_title(self,value):
        if not value or value =="":
            raise serializers.ValidationError("Title cannot be empty")
        return bleach.clean(value)
    
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price', 'featured', 'price', 'category', 'category_id' ]
        extra_kwargs = {
            'price': {'min_value' : 0},
            'validators': [
                UniqueValidator(queryset = MenuItem.objects.all()),
            ]
        }
        
class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), write_only=True, source='menuitem'
    )
    menuitem = MenuItemSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']

    def validate(self, attrs):
        menuitem = attrs['menuitem_id']
        quantity = attrs['quantity']

        # Check if the menu item exists
        if not MenuItem.objects.filter(id=menuitem.id).exists():
            raise serializers.ValidationError("Menu item does not exist.")

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantity

        # Check if the item already exists in the cart for this user
        cart_item, created = Cart.objects.get_or_create(user=user, menuitem=menuitem)

        if not created:
            # If item already exists, update the quantity
            cart_item.quantity += quantity
            cart_item.price += price
        else:
            # If new item, set initial values
            cart_item.quantity = quantity
            cart_item.unit_price = unit_price
            cart_item.price = price

        cart_item.save()
        return cart_item
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'items']
        read_only_fields = ['id', 'user', 'total', 'date', 'items']