from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Category, Cart, CartItem, Review, Wishlist
from .serializers import ProductListSerializer, ProductDetailSerializer, CategoryDetailSerializer, CategoryListSerializer, CartSerializer, CartItemSerializer,ReviewSerializer, WishlistSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
# Create your views here.
User = get_user_model()

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


## Add Products To The Cart throught cart_code and product_code
@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)
    cartitem, created = CartItem.objects.get_or_create(product =product, cart = cart)
    cartitem.quantity = 1
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
    quantity = int(quantity)

    cartitem = CartItem.objects.get(id= cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({
    "data": serializer.data,
    "message": "Cart Item updated successfully" })


@api_view(['POST'])
def add_review(request):
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating  = request.data.get("rating")
    review_text = request.data.get("review")

    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)
    if Review.objects.filter(product=product, user=user).exists():
        return Response({"error": "You already dropped a review for this product"}, status=400)

    review, created = Review.objects.update_or_create(
        product=product,
        user=user,
        defaults={
            "rating": rating,
            "review": review_text
        }
    )

    serializer = ReviewSerializer(review)
    message = "Review created successfully" if created else "Review updated successfully"

    return Response({
        "data": serializer.data,
        "message": message
    })


@api_view(['PUT'])
def update_review(request, pk):
    review_obj = Review.objects.get(id=pk)  # get the actual Review instance
    
    new_rating = request.data.get("rating")
    new_text = request.data.get("review")

    if new_rating is not None:
        review_obj.rating = new_rating
    if new_text is not None:
        review_obj.review = new_text

    review_obj.save()
    serializer = ReviewSerializer(review_obj)
    return Response(serializer.data)



@api_view(['DELETE'])
def delete_review(request, pk):
    review = Review.objects.get(id=pk)
    review.delete()

    return Response("Review Deleted Succssfully", status=204)


@api_view(['DELETE'])
def delete_cartitem(request, pk):
    cartitem = CartItem.objects.get(id=pk)
    cartitem.delete()

    return Response("cart item Deleted Succssfully", status=204)


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get("email")
    product_id = request.data.get("product_id")
    user = User.objects.get(email=email)
    
    product = Product.objects.get(id=product_id)
    
    ## Check if there is a wishlist for this product or not  
    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()
        return Response("Wishlist deleted successfully!", status=204)

    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)


@api_view(['GET'])
def product_search(request):
    query = request.query_params.get("query")  # DRF way
    if not query:
        return Response({"error": "There is no query provided!"}, status=400)
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)
       

