from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from store.models import Book, Category, Writer
from .models import Order, OrderItem, Customer, Cart, Requisition, Review, Wishlist

from django.db.models import Count  # ✅ Add this import
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
from collections import Counter
from django.db.models import Count, Avg  # ✅ Import Avg

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



@login_required(login_url='login')
def e_purse_checkout(request, order_id):
    customer = request.user.customer  # Get logged-in customer
    order = get_object_or_404(Order, id=order_id, customer=customer)
    cart_items = Cart.objects.filter(user=request.user)  # Get user's cart items

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        country = request.POST.get("country", "").strip()

        # Validate shipping address
        if not address or not state or not pincode or not country:
            messages.error(request, "⚠️ Please fill in all the shipping address fields.")
            return redirect("e_purse_checkout", order_id=order.id)

        # ✅ Check stock availability and adjust cart quantity
        stock_adjusted = False
        for cart_item in cart_items:
            if cart_item.book.stock < cart_item.quantity:
                messages.warning(request, f"⚠️ Not enough stock for {cart_item.book.name}. Only {cart_item.book.stock} left.")
                cart_item.quantity = cart_item.book.stock  # Adjust cart quantity to available stock
                cart_item.save()
                stock_adjusted = True

        if stock_adjusted:
            return redirect("cart_view")  # Redirect user back to cart

        # Check if E-Purse balance is sufficient
        if customer.e_purse_balance >= order.total_price:
            customer.e_purse_balance -= order.total_price
            customer.save()

            # Save shipping address and mark order as paid
            order.status = "Paid"
            order.payment_mode = "E-Purse"
            order.address = f"{address}, {state}, {pincode}, {country}"
            order.save()

            # ✅ Insert items from cart into OrderItem table & Reduce Stock
            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price * cart_item.quantity
                )

                order_items.append(order_item)  # Collect items for email

                cart_item.book.stock -= cart_item.quantity
                cart_item.book.save()

            # ✅ Clear the user's cart
            cart_items.delete()

            # ✅ Send Email Notification
            subject = "📚 BookHaven: Your Order Confirmation"
            customer_email = request.user.email  # Get user's email

            # Render HTML email template
            html_message = render_to_string("emails/order_confirmation.html", {
                "customer": customer,
                "order": order,
                "order_items": order_items,
                "company_name": "BookHaven",
                "company_logo": f"{settings.STATIC_URL}images/bookhaven_logo.png"
            })
            plain_message = strip_tags(html_message)  # Convert HTML to plain text

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,  # Sender email (configured in settings)
                [customer_email],  # Recipient email
                html_message=html_message
            )

            messages.success(request, "✅ Payment successful! Your order has been placed.")
            return redirect("order_success")  # Redirect to success page
        else:
            messages.error(request, "⚠️ Insufficient E-Purse balance.")
            return redirect("e_purse_checkout", order_id=order.id)

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/checkout.html",
        "order": order,
        "customer": customer
    })


@login_required(login_url='login')
def order_success(request):
    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/order_success.html"
    })


@login_required(login_url='login')
def add_to_requisition(request, book_id):
    """Handles adding a book to the requisition table"""
    customer = request.user.customer  # Get logged-in customer
    book = get_object_or_404(Book, id=book_id)

    # Check if requisition already exists
    existing_requisition = Requisition.objects.filter(customer=customer, book=book).first()
    if existing_requisition:
        messages.warning(request, "⚠️ You have already requested this book.")
        return redirect("book_detail", book_id=book.id)

    # Create a new requisition
    requisition = Requisition.objects.create(
        customer=customer,
        book=book,
        book_name=book.name,
        author_names=", ".join([author.name for author in book.authors.all()])
    )

    messages.success(request, "✅ Book has been added to your requisition list.")
    return redirect("requisition_list")  # Redirect to the user's requisition list


@login_required(login_url='login')
def requisition_list(request):
    """Displays the list of requisitioned books for the logged-in user"""
    customer = request.user.customer  # Get logged-in customer
    requisitions = Requisition.objects.filter(customer=customer).order_by("-requested_at")

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/requisition_list.html",
        "requisitions": requisitions
    })


@login_required(login_url='login')
def submit_review(request, book_id):
    """Handles review submission and editing"""
    customer = request.user.customer
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        description = request.POST.get("description", "").strip()

        # ✅ Ensure rating is provided
        if not rating:
            messages.error(request, "⚠️ Please select a rating before submitting your review.")
            return redirect("book_detail", book_id=book.id)

        # ✅ Convert rating to Decimal type safely
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            messages.error(request, "⚠️ Invalid rating value. Please choose a valid rating.")
            return redirect("book_detail", book_id=book.id)

        # ✅ Ensure rating is within 1-5 range
        if rating < 1 or rating > 5:
            messages.error(request, "⚠️ Rating must be between 1 and 5 stars.")
            return redirect("book_detail", book_id=book.id)

        # ✅ Delete any existing review to avoid duplicate issues
        Review.objects.filter(customer=customer, book=book).delete()

        # ✅ Create a new review with proper validation
        review = Review.objects.create(
            customer=customer,
            book=book,
            rating=rating,  # ✅ Ensures rating is set properly
            description=description
        )

        messages.success(request, "✅ Your review has been submitted!")
        return redirect("book_detail", book_id=book.id)



@login_required(login_url='login')
def delete_review(request, review_id):
    """Allow users to delete their own review"""
    review = get_object_or_404(Review, id=review_id, customer=request.user.customer)
    book_id = review.book.id
    review.delete()

    messages.success(request, "❌ Your review has been deleted.")
    return redirect("book_detail", book_id=book_id)


@login_required(login_url='login')
def order_history(request):
    """Fetch and display the user's order history"""
    customer = request.user.customer  # Get logged-in customer
    orders = Order.objects.filter(customer=customer).order_by("-timestamp")  # Get orders (newest first)

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/order_history.html",
        "orders": orders
    })


@login_required(login_url='login')
def recommended_books(request):
    """Generate book recommendations using ML, wishlist, & traditional filtering"""
    customer = request.user.customer  # Get logged-in customer

    # ✅ Step 1: Get Ordered, Requisitioned, & Wishlisted Books
    ordered_books = OrderItem.objects.filter(order__customer=customer).values_list('book', flat=True)
    requisitioned_books = Requisition.objects.filter(customer=customer).values_list('book', flat=True)
    wishlist_books = Wishlist.objects.filter(user=request.user).values_list('book', flat=True)  # ✅ Fixed error

    # Merge all book IDs
    book_ids = set(ordered_books) | set(requisitioned_books) | set(wishlist_books)

    if book_ids:
        books = Book.objects.filter(id__in=book_ids, stock__gt=0)  # ✅ Exclude out-of-stock books

        # Get frequently appearing categories & authors
        categories = books.values_list('categories', flat=True)
        authors = books.values_list('authors', flat=True)

        top_categories = [c[0] for c in Counter(categories).most_common(3)]
        top_authors = [a[0] for a in Counter(authors).most_common(3)]

        # ✅ Recommend books based on category (fallback to random)
        category_books = Book.objects.filter(categories__in=top_categories, stock__gt=0).exclude(id__in=book_ids).distinct()
        if not category_books.exists():
            category_books = Book.objects.filter(stock__gt=0).order_by("?")[:4]  # ✅ Return random books if empty

        # ✅ Recommend books based on author (fallback to random)
        author_books = Book.objects.filter(authors__in=top_authors, stock__gt=0).exclude(id__in=book_ids).distinct()
        if not author_books.exists():
            author_books = Book.objects.filter(stock__gt=0).order_by("?")[:4]  # ✅ Return random books if empty
    else:
        # ✅ If No Order/Requisition/Wishlist, Suggest Random Books
        category_books = Book.objects.filter(stock__gt=0).order_by("?")[:4]
        author_books = Book.objects.filter(stock__gt=0).order_by("?")[:4]

    # ✅ Step 4: Suggest 4 Most Popular Books
    popular_books = Book.objects.filter(stock__gt=0).annotate(total_sales=Count('orderitem')).order_by('-total_sales')[:4]

    # ✅ Step 5: Apply ML-Based Recommendations (Apriori)
    transactions = []
    orders = OrderItem.objects.all().values('order_id', 'book_id')

    # Build transaction list for Apriori
    transaction_dict = {}
    for order in orders:
        transaction_dict.setdefault(order['order_id'], []).append(str(order['book_id']))
    
    transactions = list(transaction_dict.values())

    ml_recommended_books = []
    if transactions:
        try:
            # ✅ Convert to DataFrame
            df = pd.DataFrame(transactions).fillna(0)

            # ✅ Convert to Binary Format (0 or 1)
            book_dummy = pd.get_dummies(df.stack()).groupby(level=0).sum()
            book_dummy = book_dummy.astype(bool)

            # ✅ Apply Apriori Algorithm
            frequent_itemsets = apriori(book_dummy, min_support=0.1, use_colnames=True)
            rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)

            # ✅ Get Strongly Associated Books
            if not rules.empty:
                book_ids = set()
                for itemset in rules.sort_values('lift', ascending=False).head(5)['consequents']:
                    book_ids.update(itemset)

                ml_recommended_books = Book.objects.filter(id__in=book_ids, stock__gt=0)  # ✅ Exclude out-of-stock books

        except Exception as e:
            print(f"ML Recommendation Error: {e}")  # ✅ Log error (avoid breaking system)

    # ✅ Combine All Recommendations (Ensuring Uniqueness)
    recommended_books = list(set(popular_books) | set(category_books) | set(author_books) | set(ml_recommended_books))

    # ✅ Ensure at least 4 books are recommended (fallback to random if needed)
    if len(recommended_books) < 4:
        extra_books = Book.objects.filter(stock__gt=0).order_by("?")[: (4 - len(recommended_books))]
        recommended_books.extend(extra_books)

    # ✅ Calculate Average Ratings for Each Recommended Book
    recommended_books = Book.objects.filter(id__in=[book.id for book in recommended_books]).annotate(avg_rating=Avg('review__rating'))

    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/recommendations.html",
        "recommended_books": recommended_books,
        "popular_books": popular_books,
        "category_books": category_books,
        "author_books": author_books,
        "range": range(1, 6)  # ✅ Pass range from 1 to 5
    })


@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    messages.success(request, f"Added to Wishlist")
    return redirect('book_detail', book_id=book_id)

@login_required
def remove_from_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.filter(user=request.user, book=book).delete()
    messages.success(request, f"Removed from Wishlist")
    return redirect('book_detail', book_id=book_id)

@login_required
def wishlist(request):
    wishlist_books = Wishlist.objects.filter(user=request.user)
    return render(request, "dashboard/main.html", {
        "template_name": "dashboard/wishlist.html",
        "wishlist_books": wishlist_books
    })