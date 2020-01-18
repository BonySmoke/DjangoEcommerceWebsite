from django.contrib import admin
from .models import Product, OrderProduct, OrderList, BillingAddress, PaymentInformation, Comment, Coupon


class OrderListAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

#modifies the displayed fields. Adds the boolean <ordered>: True, False
class OrderProductAdmin(admin.ModelAdmin):
    #list_display is the convention
    list_display = ['product', 'ordered']

#registers all the Models in django admin
admin.site.register(Product)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(OrderList, OrderListAdmin)
admin.site.register(BillingAddress)
admin.site.register(PaymentInformation)
admin.site.register(Comment)
admin.site.register(Coupon)
