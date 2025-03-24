from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from store.models import Book
from .models import Order, OrderItem, Customer, Cart, Requisition, Review


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

        # If stock was adjusted, redirect to the cart page
        if stock_adjusted:
            return redirect("cart_view")  # ✅ Redirect user back to cart

        # Check if E-Purse balance is sufficient
        if customer.e_purse_balance >= order.total_price:
            # Deduct the amount from E-Purse
            customer.e_purse_balance -= order.total_price
            customer.save()

            # Save the full shipping address and mark order as paid
            order.status = "Paid"
            order.payment_mode = "E-Purse"
            order.address = f"{address}, {state}, {pincode}, {country}"
            order.save()

            # ✅ Insert items from cart into OrderItem table & Reduce Stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price * cart_item.quantity  # Store total price of that item
                )

                # ✅ Reduce book stock
                cart_item.book.stock -= cart_item.quantity
                cart_item.book.save()

            # ✅ Clear the user's cart
            cart_items.delete()

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