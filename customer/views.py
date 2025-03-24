from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem, Customer, Cart


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
