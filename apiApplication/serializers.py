from rest_framework import serializers
from .models import Product, Category, CartItem, Cart, Review, Wishlist
from django.contrib.auth import get_user_model

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'image', 'price'] 


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','description' ,'slug', 'image', 'price'] 


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many = True, read_only = True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'products']



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only = True)
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'sub_total' , 'quantity' ]

    def get_sub_total(self, cartItem):
        total = cartItem.product.price * cartItem.quantity
        return total
    
class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(read_only = True, many = True)
    cart_total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'cart_items', 'cart_total']

    def get_cart_total(self, cart):
        items = cart.cart_items.all()
        total = sum([item.quantity * item.product.price for item in items ])
        return total
        

class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    class Meta: 
        model = Cart
        fields = ['id', 'cart_code', 'total_quantity']
    def get_cart_total(self, cart):
        items = cart.cart_items.all()
        total = sum([item.quantity for item in items ])
        return total


## The One Who Made The Review
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "profile_pic_url"]

## The Actual Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only= True)
    class Meta:
        model = Review
        fields = ["id",  "rating", "review", "created", "updated", "user"]


class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "created"]

