from django.utils.text import slugify
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
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
    menuitem = MenuItemSerializer(read_only=True)
    #user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
    