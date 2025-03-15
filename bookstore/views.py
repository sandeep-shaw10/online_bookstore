from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from store.models import Book, Writer, Category
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from customer.models import Customer
from decimal import Decimal

# Public Home Page
def home(request):
    categories = Category.objects.all()
    return render(request, 'home.html', {
        "categories": categories
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


@login_required(login_url='login')
def dashboard_shop(request):
    query = request.GET.get("q", "").strip()
    search_by = request.GET.get("search_by", "name")  # Default: Search by Name
    selected_category = request.GET.get("category", "")  # Get selected category

    books = Book.objects.all()
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

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/shop.html",
        "books": books,
        "query": query,
        "search_by": search_by,
        "categories": categories,  # Pass categories to template
        "selected_category": selected_category  # Keep track of selected category
    })


@login_required(login_url='login')
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/book_detail.html", 
        "book": book
    })
# Authentication -----------------



@login_required
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

@login_required
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