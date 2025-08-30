from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Category, Cart, CartItem, Review, Wishlist
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, CategoryDetailSerializer, 
    CategoryListSerializer, CartSerializer, CartItemSerializer,
    ReviewSerializer, WishlistSerializer
)
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer


# Get the custom User model
User = get_user_model()


# ==============================
# PRODUCT VIEWS
# ==============================

# Get all featured products
@api_view(['GET'])
def product_list(requset):
    # Fetch all products where featured=True
    products = Product.objects.filter(featured=True)
    # Serialize data into JSON format
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


# Get single product details using slug
@api_view(['GET'])
def product_detail(requst, slug):
    # Fetch one product using its slug
    products = Product.objects.get(slug=slug)
    # Serialize single product
    serializer = ProductDetailSerializer(products)
    return Response(serializer.data)


# ==============================
# CATEGORY VIEWS
# ==============================

# Get all categories
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


# Get single category details using slug
@api_view(['GET'])
def category_detail(requset, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)


# ==============================
# CART & CARTITEM VIEWS
# ==============================

# Add product to cart (by cart_code and product_id)
@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')    # Unique cart identifier
    product_id = request.data.get('product_id')  # Product ID to add

    # Create or get existing cart
    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    # Fetch the product
    product = Product.objects.get(id=product_id)
    # Create or get cart item
    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    # Default quantity set to 1
    cartitem.quantity = 1
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


# Update cart item quantity
@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('item_id')  # ID of cart item
    quantity = request.data.get('quantity')    # New quantity
    quantity = int(quantity)

    # Fetch cart item and update quantity
    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({
        "data": serializer.data,
        "message": "Cart Item updated successfully"
    })


# Delete cart item
@api_view(['DELETE'])
def delete_cartitem(request, pk):
    cartitem = CartItem.objects.get(id=pk)
    cartitem.delete()
    return Response("cart item Deleted Succssfully", status=204)


# ==============================
# REVIEW VIEWS
# ==============================

# Add a new review or update existing one
@api_view(['POST'])
def add_review(request):
    product_id = request.data.get("product_id")  # Product being reviewed
    email = request.data.get("email")            # User email
    rating = request.data.get("rating")          # Rating value
    review_text = request.data.get("review")     # Review text

    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)

    # Prevent duplicate review (user can only review once per product)
    if Review.objects.filter(product=product, user=user).exists():
        return Response({"error": "You already dropped a review for this product"}, status=400)

    # Create or update review
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


# Update an existing review by ID
@api_view(['PUT'])
def update_review(request, pk):
    review_obj = Review.objects.get(id=pk)  # Get review instance

    # New data
    new_rating = request.data.get("rating")
    new_text = request.data.get("review")

    # Update only provided fields
    if new_rating is not None:
        review_obj.rating = new_rating
    if new_text is not None:
        review_obj.review = new_text

    review_obj.save()
    serializer = ReviewSerializer(review_obj)
    return Response(serializer.data)


# Delete a review
@api_view(['DELETE'])
def delete_review(request, pk):
    review = Review.objects.get(id=pk)
    review.delete()
    return Response("Review Deleted Succssfully", status=204)


# ==============================
# WISHLIST VIEWS
# ==============================

# Add or remove product from wishlist
@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get("email")
    product_id = request.data.get("product_id")

    # Get user and product
    user = User.objects.get(email=email)
    product = Product.objects.get(id=product_id)

    # Check if already in wishlist -> remove it
    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()
        return Response("Wishlist deleted successfully!", status=204)

    # Else -> add to wishlist
    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)


# ==============================
# SEARCH VIEW
# ==============================

# Search products by name, description, or category
@api_view(['GET'])
def product_search(request):
    query = request.query_params.get("query")  # Get ?query=... from URL
    if not query:
        return Response({"error": "There is no query provided!"}, status=400)
    
    # Perform search across product fields and related category
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()  # Ensure no duplicates

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)



@api_view(["POST"])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "User registered successfully!",
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login
@api_view(["POST"])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "message": "Login successful!",
            "user": UserProfileSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
