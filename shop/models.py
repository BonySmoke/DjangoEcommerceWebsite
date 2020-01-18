from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
from django.db.models.signals import pre_save
from .utils import unique_transaction_id_generator, get_unique_slug


class Product(models.Model):
    title = models.CharField(max_length=150)
    discription = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    discount_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(default='default.jpg', upload_to='product_pics')
    status = models.CharField(max_length=15, default="ordinary")
    category = models.CharField(max_length=20, default="no category")
    com = models.ForeignKey('Comment', on_delete=models.SET_NULL,
                            blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={'slug': self.slug})


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_product_price(self):
        if self.product.discount_price:
            return self.quantity * self.product.discount_price
        return self.quantity * self.product.price

    def get_total_discount_product_price(self):
        return self.quantity * self.product.discount_price

    def get_saved_amount(self):
        return self.get_total_product_price - self.get_total_discount_product_price


class OrderList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL,
                                blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True,
        related_name='remove_coupon')

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_product_price()
        if self.coupon != None and self.coupon.discount_amount_dollar > 0.0:
            total -= self.coupon.discount_amount_dollar
            return total
        elif self.coupon and self.coupon.discount_amount_percent:
            decrease_amount = (total / 100) * int(self.coupon.discount_amount_percent)
            total -= decrease_amount
            return total
        else:
            return total
        return total


class BillingAddress(models.Model):
    firstname = models.CharField(max_length=100, default='Name')
    lastname = models.CharField(max_length=100, default='Surname')
    phone_number = models.CharField(max_length=100, default='Number')
    email_address = models.CharField(max_length=100, default='Email')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = CountryField(multiple=False)
    payment = models.ForeignKey('PaymentInformation', on_delete=models.SET_NULL,
                                blank=True, null=True)
    save_info = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class PaymentInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ForeignKey(OrderList, on_delete=models.CASCADE)
    transaction = models.CharField(max_length=120, blank=True)
    #billed_date = models.DateTimeField(auto_now_add=True)
    card_number = models.CharField(default='0000000000000000', null=True, max_length=16)
    card_name = models.CharField(max_length=25, default='VISA')
    exp_date = models.CharField(max_length=30, default='dd/mm/year')
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return self.user.username

# creates a payment transaction before saving the form


def pre_save_create_transaction(sender, instance, *args, **kwargs):
    if not instance.transaction:
        instance.transaction = unique_transaction_id_generator(instance)


pre_save.connect(pre_save_create_transaction, sender=PaymentInformation)


class Comment(models.Model):
    username = models.CharField(max_length=30)
    context = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    positive = models.TextField()
    negative = models.TextField()
    prod = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                   related_name='comment_likes')

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'user', 'slug')
        super().save(*args, **kwargs)

    def get_comment_like_url(self):
        return reverse("comment-like", kwargs={'slug': self.slug})

class Coupon(models.Model):
    coupon = models.CharField(max_length=20, blank=True, null=True)
    discount_amount_dollar = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discount_amount_percent = models.CharField(max_length=3, blank=True, null=True)
    discription = models.TextField(default="Gives a discount")

    def __str__(self):
        return self.coupon
