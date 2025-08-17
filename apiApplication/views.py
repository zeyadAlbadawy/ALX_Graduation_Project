from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Category
from .serializers import ProductListSerializer, ProductDetailSerializer, CategoryDetailSerializer, CategoryListSerializer
# Create your views here.

# get all the product list
@api_view(['GET'])
def product_list(requset):
    products = Product.objects.filter(featured = True)
    serializer = ProductListSerializer(products, many = True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(requst, slug):
    products = Product.objects.get(slug = slug)
    serializer = ProductDetailSerializer(products)
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(requset, slug):
    category = Category.objects.get(slug = slug)
    serializer =CategoryDetailSerializer(category)
    return Response(serializer.data)