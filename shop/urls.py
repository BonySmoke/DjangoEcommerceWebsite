from django.urls import path
from .import views
from .views import (
    Detail, List, OrderSummary, Checkout, Payment, CommentCreate,)
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import login_view, register_view, logout_view


urlpatterns = [
    path('', List.as_view(), name="shop-main"),
    path('category/<str:category>', views.category_list, name="shop-category"),
    path('product/<slug:slug>/', Detail.as_view(), name="product-detail"),
    path('add_to_cart/<slug:slug>/', views.add_to_cart, name="add_to_cart"),
    path('remove_from_cart/<slug:slug>/', views.remove_from_cart, name="remove_from_cart"),
    path('remove_one_product_from_cart/<slug:slug>/', views.remove_one_product_from_cart, name="remove_one_from_cart"),
    path('order_summary/', OrderSummary.as_view(), name='order_summary'),
    path('order_checkout/', Checkout.as_view(), name='order_checkout'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/register/', register_view, name='register'),
    path('accounts/logout/', logout_view, name='logout'),
    path('order_checkout/<payment_option>/', Payment.as_view(), name='payment'),
    path('order_checkout/credit card/email/', views.email, name='email'),
    path('product/<slug:slug>/create/', CommentCreate.as_view(), name='comment'),
    path('comment_like/<slug:slug>/', views.comment_like, name='comment-like'),
    path('apply_coupon/', views.apply_coupon, name='add-coupon'),
    path('remove_coupon/', views.remove_coupon, name='remove-coupon'),
    path('coupon', views.coupon_list, name='coupon_list'),
    path('about_us', views.about, name='about-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
