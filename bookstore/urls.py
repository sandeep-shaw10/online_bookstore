"""
URL configuration for bookstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from customer.views import *
from .views import *
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = "Online Book Store Admin"  
admin.site.site_title = "Book Store Admin Portal"  
admin.site.index_title = "Welcome to Book Store Dashboard"


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/profile', dashboard_profile, name='dashboard_profile'),
    path('dashboard/epurse', dashboard_epurse, name='dashboard_epurse'),
    path('dashboard/shop', dashboard_shop, name='dashboard_shop'),
    path("dashboard/shop/book/<int:book_id>/", book_detail, name="book_detail"),
    path("dashboard/profile/", profile, name="profile"),
    path("add-money/", add_money, name="add_money"),
    path('dashboard/cart/', cart_view, name='cart_view'),
    path('dashboard/cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('dashboard/cart/remove/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('dashboard/cart/increase/<int:cart_id>/', increase_quantity, name='increase_quantity'),
    path('dashboard/cart/decrease/<int:cart_id>/', decrease_quantity, name='decrease_quantity'),
    path('checkout/<int:order_id>/', e_purse_checkout, name='e_purse_checkout'),
    path('order-success/', order_success, name='order_success'),
    path('requisition/add/<int:book_id>/', add_to_requisition, name='add_to_requisition'),
    path('requisition/list/', requisition_list, name='requisition_list'),
    path('review/submit/<int:book_id>/', submit_review, name='submit_review'),
    path('review/delete/<int:review_id>/', delete_review, name='delete_review'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)