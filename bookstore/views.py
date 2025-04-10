from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg, Sum, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from store.models import Book, Writer, Category
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from customer.models import Cart, Order, Customer, OrderItem, Requisition, Review
from decimal import Decimal
import random
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import F, Sum, FloatField
import json



# Function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_staff 

# Public Home Page
def home(request):
    query = request.GET.get("q", "").strip()
    search_by = request.GET.get("search_by", "name")
    selected_category = request.GET.get("category", "")

    categories = Category.objects.all()
    featured_books = list(Book.objects.filter(featured=True))
    random_featured_books = random.sample(featured_books, min(4, len(featured_books)))
    latest_books = Book.objects.order_by('-id')[:4]

    # If a search query is present, redirect to the shop page with parameters
    if query or selected_category:
        return redirect(f"/dashboard/shop?q={query}&search_by={search_by}&category={selected_category}")
    
    return render(request, 'home.html', {
        "categories": categories,
        "featured_books": random_featured_books,
        "latest_books": latest_books
    })


# Authentication -----------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    error = ''
    if request.method == 'POST':
        username = request.POST['user']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            error = "Passwords do not match!"
        elif User.objects.filter(username=username).exists():
            error = "Username already taken!"
        elif User.objects.filter(email=email).exists():
            error = "Email already registered!"
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect("dashboard")

    context = { "error": error }
    return render(request, 'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    error = ''
    if request.method == 'POST':
        username = request.POST['user']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid Credentials"
    
    context = { "error": error }
    return render(request, 'auth/login.html', context)


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, "dashboard/main.html", {"template_name": "dashboard/hello.html"})


@login_required(login_url='login')
def dashboard_profile(request):
    return render(request, "dashboard/main.html", {"template_name": "dashboard/profile.html"})

@login_required(login_url='epurse')
def dashboard_epurse(request):
    return render(request, "dashboard/main.html", {"template_name": "dashboard/epurse.html"})


@login_required(login_url='login')
def dashboard_shop(request):
    query = request.GET.get("q", "").strip()
    search_by = request.GET.get("search_by", "name")  # Default: Search by Name
    selected_category = request.GET.get("category", "")  # Get selected category

    books = Book.objects.annotate(avg_rating=Avg('review__rating'))  # ✅ Exclude out-of-stock books
    categories = Category.objects.all()  # Get all categories

    # Apply search filters
    if query:
        if search_by == "name":
            books = books.filter(name__icontains=query)
        elif search_by == "author":
            books = books.filter(authors__name__icontains=query)

    # Apply category filter if selected
    if selected_category:
        books = books.filter(categories__id=selected_category)

    # Sort books by highest rating first
    books = books.order_by('-avg_rating')

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/shop.html",
        "books": books,
        "query": query,
        "search_by": search_by,
        "categories": categories,
        "selected_category": selected_category,
        "range": range(1, 6)  # ✅ Pass range from 1 to 5
    })


@login_required(login_url='login')
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart_items = Cart.objects.filter(user=request.user).values_list('book_id', flat=True)
    reviews = Review.objects.filter(book=book).order_by("-timestamp")

    # ✅ Fetch the logged-in user's review, if it exists
    user_review = Review.objects.filter(book=book, customer=request.user.customer).first()

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/book_detail.html", 
        "book": book,
        "cart_items": cart_items,
        "reviews": reviews,
        "user_review": user_review  # ✅ Pass user's review to the template
    })

# Authentication -----------------



@login_required(login_url='login')
def profile(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        address = request.POST.get("address", "").strip()

        user = request.user
        customer = request.user.customer

        if full_name:
            first_name, last_name = (full_name.split(" ", 1) + [""])[:2]
            user.first_name = first_name
            user.last_name = last_name

        if address:
            customer.address = address

        if new_password:
            user.set_password(new_password)
            update_session_auth_hash(request, user)  # Keep the user logged in after password change

        user.save()
        customer.save()
        messages.success(request, "Profile updated successfully!")

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/profile.html"
    })

@login_required(login_url='login')
def add_money(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = Decimal(amount)  # Convert to Decimal
            if amount > 0:
                request.user.customer.e_purse_balance += amount
                request.user.customer.save()
                messages.success(request, f"${amount} added to your E-Purse!")
            else:
                messages.error(request, "Invalid amount!")
        except:
            messages.error(request, "Enter a valid number!")
    
    return redirect("profile")


## CART -----------------
@login_required(login_url='login')
def add_to_cart(request, book_id):
    book = Book.objects.get(id=book_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)

    if not created:
        cart_item.quantity += 1  # Increase quantity if book is already in cart
        cart_item.save()
    
    messages.success(request, "Book added to cart!")
    return redirect('cart_view')  # Redirect to cart page


@login_required(login_url='login')
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)

    # Get the Customer instance
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Create or get an existing pending order
    order, created = Order.objects.get_or_create(customer=customer, status="Pending", defaults={"total_price": total_price, "payment_mode": "E-Purse", "address": "User Address"})

    # Update order total price if it changed
    if not created:
        order.total_price = total_price
        order.save()

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/cart.html",
        "cart_items": cart_items,
        "total_price": total_price,
        "order": order  # ✅ Pass the order object to the template
    })


@login_required(login_url='login')
def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()
    
    if not cart_item:
        messages.error(request, "Item not found in your cart.")
        return redirect('cart_view')

    cart_item.delete()
    messages.success(request, "Item removed from cart!")
    return redirect('cart_view')


@login_required(login_url='login')
def increase_quantity(request, cart_id):
    cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')


@login_required(login_url='login')
def decrease_quantity(request, cart_id):
    cart_item = Cart.objects.filter(id=cart_id, user=request.user).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()  # Remove if quantity is 1 and user clicks decrease
    return redirect('cart_view')


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')  # Redirect non-admins to login
def analytics(request):
    books_sold = OrderItem.objects.count()  
    total_books_sold = OrderItem.objects.aggregate(total=Sum("quantity"))["total"] or 0  

    total_revenue = Order.objects.filter(status="Paid").aggregate(total=Sum("total_price"))["total"] or 0
    total_revenue = f"{total_revenue:.2f}"

    total_orders = Order.objects.count()
    total_requisitions = Requisition.objects.count()
    total_users = User.objects.count()

    categories = (
        OrderItem.objects
        .values("book__categories__name")  # Fetch category names, not IDs
        .annotate(total_revenue=Sum(F("price"), output_field=FloatField()))
    )

    category_data = {
        cat["book__categories__name"]: round(cat["total_revenue"], 2)
        for cat in categories
    }

    today = now()

    # Revenue calculations with Decimal to float conversion
    def get_revenue(queryset):
        total = queryset.aggregate(total=Sum("total_price"))["total"] or Decimal(0)
        return float(total)  # Convert to float to make it JSON serializable

    revenue_today = get_revenue(Order.objects.filter(status="Paid", timestamp__date=today.date()))
    revenue_this_week = get_revenue(Order.objects.filter(status="Paid", timestamp__gte=today - timedelta(days=7)))
    revenue_this_month = get_revenue(Order.objects.filter(status="Paid", timestamp__gte=today - timedelta(days=30)))
    revenue_last_3_months = get_revenue(Order.objects.filter(status="Paid", timestamp__gte=today - timedelta(days=90)))
    revenue_this_year = get_revenue(Order.objects.filter(status="Paid", timestamp__gte=today - timedelta(days=365)))
    revenue_overall = get_revenue(Order.objects.filter(status="Paid"))

    # Store revenue data in JSON-safe format
    revenue_data = {
        "today": round(revenue_today, 2),
        "this_week": round(revenue_this_week, 2),
        "this_month": round(revenue_this_month, 2),
        "last_3_months": round(revenue_last_3_months, 2),
        "this_year": round(revenue_this_year, 2),
        "overall": round(revenue_overall, 2),
    }

    context = {
        "books_sold": books_sold,
        "total_books_sold": total_books_sold,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_requisitions": total_requisitions,
        "total_users": total_users,
        "template_name": "dashboard/analytics.html",
        "revenue_data": json.dumps(revenue_data),
        "category_data": json.dumps(category_data)
    }

    return render(request, "dashboard/main.html", context)