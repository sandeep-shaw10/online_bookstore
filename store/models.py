from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Writer(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='writers/', blank=True, null=True)
    about = models.TextField()

    def __str__(self):
        return self.name

    def image_tag(self):  # This method returns an HTML image tag
        if self.image:
            return f'<img src="{self.image.url}" width="100" height="100" style="border-radius: 10px;" />'
        return "No Image"

    image_tag.allow_tags = True  # Needed for Django <4.0
    image_tag.short_description = 'Writer Image'  # Label in admin panel


class Book(models.Model):
    name = models.CharField(max_length=255)
    authors = models.ManyToManyField(Writer)
    summary = models.TextField()
    categories = models.ManyToManyField(Category)
    cover_image = models.ImageField(upload_to='books/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    # New fields
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)  # ISBN (optional)
    edition = models.CharField(max_length=50, blank=True, null=True)  # Edition (e.g., "2nd Edition")
    publisher = models.CharField(max_length=255, blank=True, null=True)  # Publisher Name
    publication_year = models.PositiveIntegerField(blank=True, null=True)  # Year of Publication
    
    # Featured field
    featured = models.BooleanField(default=False, null=True, blank=True)  # Allows null & blank values

    def __str__(self):
        return f"{self.name} ({self.edition})" if self.edition else self.name

    def cover_image_tag(self):  # Preview for book cover in admin
        if self.cover_image:
            return f'<img src="{self.cover_image.url}" width="100" height="150" style="border-radius: 10px;" />'
        return "No Image"

    cover_image_tag.allow_tags = True
    cover_image_tag.short_description = 'Cover Preview'