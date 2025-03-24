from django.contrib import admin
from django.utils.html import mark_safe  # Needed for Django 4.x+
from .models import Category, Writer, Book

@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag')  # Show image in the list
    readonly_fields = ('image_tag',)  # Show image in the detail view
    search_fields = ('name',)  # Search functionality for Writer name
    ordering = ('name',)  # Sort by Writer name by default

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" style="border-radius: 10px;" />')
        return "No Image"

    image_tag.short_description = 'Writer Image'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_authors', 'cover_image_tag', 'price', 'stock')  # Added authors
    readonly_fields = ('cover_image_tag',)
    list_filter = ('categories', 'authors','featured')  # Filter books by category and authors
    search_fields = ('name', 'authors__name')  # Search by book name or author name
    ordering = ('name', 'price', 'stock')  # Default sorting by name, then price, then stock

    def display_authors(self, obj):
        return ", ".join([author.name for author in obj.authors.all()])  # Fetch all authors' names

    display_authors.short_description = 'Authors'
    display_authors.admin_order_field = 'authors__name'  # Allow sorting by author names

    def cover_image_tag(self, obj):
        if obj.cover_image:
            return mark_safe(f'<img src="{obj.cover_image.url}" width="100" height="150" style="border-radius: 10px;" />')
        return "No Image"

    cover_image_tag.short_description = 'Cover Preview'

admin.site.register(Category)