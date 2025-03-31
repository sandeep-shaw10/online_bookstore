from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from customer.models import Requisition
from store.models import Book

# Dictionary to track previous stock values
previous_stock_values = {}

@receiver(pre_save, sender=Book)
def track_previous_stock(sender, instance, **kwargs):
    """Stores the previous stock value before saving"""
    if instance.id:  # Ensure it's an existing book (not a new one)
        try:
            previous_stock_values[instance.id] = Book.objects.get(id=instance.id).stock
        except Book.DoesNotExist:
            previous_stock_values[instance.id] = 0  # Default to 0 if book doesn't exist

@receiver(post_save, sender=Book)
def notify_users_on_stock_update(sender, instance, created, **kwargs):
    """Checks if stock was 0 and now increased, then notifies users"""
    previous_stock = previous_stock_values.get(instance.id, 0)  # Get previous stock
    current_stock = instance.stock  # Get updated stock

    if previous_stock == 0 and current_stock > 0:  # Only trigger if stock was 0 and increased
        # Find users who requested this book
        requisitions = Requisition.objects.filter(book_name=instance.name)

        for req in requisitions:
            user_email = req.customer.user.email  # Get user email
            book_link = settings.BASE_URL + reverse("book_detail", args=[instance.id])  # Generate book link

            # Render email template
            html_message = render_to_string("emails/requisition.html", {
                "customer": req.customer,
                "book": instance,
                "book_link": book_link
            })
            plain_message = strip_tags(html_message)  # Convert to plain text

            # Send Email
            send_mail(
                subject="📖 Your Requested Book is Now Available!",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email],
                html_message=html_message  # Send HTML content
            )

            # Remove the requisition entry
            req.delete()
