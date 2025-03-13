from django.db import models
from django.contrib.auth.models import User
from store.models import Book, Category, Writer

# ✅ Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django User model
    e_purse_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Default balance 0
    address = models.TextField(null=True, blank=True)  # Optional Address
    preferred_categories = models.ManyToManyField(Category, blank=True)  # Preferred Categories
    preferred_writers = models.ManyToManyField(Writer, blank=True)  # Preferred Writers

    def __str__(self):
        return self.user.username  # Display username in admin

# ✅ Review Model (Customer reviews on Books)
class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1)  # Rating out of 5 (1.0 to 5.0)
    description = models.TextField(null=True, blank=True)  # Optional review text

    def __str__(self):
        return f'{self.customer.user.username} - {self.book.name} ({self.rating}/5)'

# ✅ Order Table (Groups all Order Items)
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total Order Price
    address = models.TextField()  # Delivery Address
    payment_mode = models.CharField(
        max_length=50, 
        choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')]
    )  # Payment Mode
    status = models.CharField(
        max_length=20, 
        choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')],
        default='Pending'
    )  # Order Status
    timestamp = models.DateTimeField(auto_now_add=True)  # Order Time

    def __str__(self):
        return f'Order #{self.id} by {self.customer.user.username} - {self.status}'

# ✅ Order Item Table (Individual Items in an Order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f'{self.book.name} (x{self.quantity}) - {self.order.customer.user.username}'

# ✅ Requisition Table (Customers request books out of stock)
class Requisition(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)  # Link to Book
    book_name = models.CharField(max_length=255)  # Store book name separately in case the book is deleted
    author_names = models.TextField(null=True, blank=True)  # Store multiple author names
    requested_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-fill author names if book is linked"""
        if self.book and not self.author_names:
            self.author_names = ", ".join([author.name for author in self.book.authors.all()])
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.book_name} requested by {self.customer.user.username}'
