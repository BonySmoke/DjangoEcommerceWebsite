from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, OrderProduct, OrderList, BillingAddress, PaymentInformation, Comment, Coupon
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, View, RedirectView
from .filters import SearchFilter
from django.utils import timezone
from .forms import CheckoutForm, PaymentForm, CommentForm, CouponForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, EmailMessage


# it's used for searching by a category using 'category'
def category_list(request, category):
    queryset = Product.objects.filter(category=category)
    product = queryset.all()
    #refers to filters.py
    filters = SearchFilter(request.GET, queryset=product)
    context = {
        'product': product,
        'filter': filters,
    }
    return render(request, "shop/laptop.html", context)

# provides a detailed view of the page


class Detail(DetailView):
    model = Product
    template_name = 'shop/product_detailed_view.html'
    context_object_name = 'product'
    product = Product.objects.all()

    def get_object(self):
        slug = self.kwargs.get("slug")
        print(slug)
        return get_object_or_404(Product, slug=slug)

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        instance = get_object_or_404(Product, slug=slug)
        #adds comments to the product instance
        context['comments'] = Comment.objects.filter(prod=instance)
        return context


# Lists all products
class List(ListView):
    model = Product
    template_name = 'shop/index.html'
    queryset = Product.objects.all()
    context_object_name = 'obj'

    # filters products by price
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #adds filters to the *home* page
        context['filter'] = SearchFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
# creates a cart with a number of ordered objects
def add_to_cart(request, slug):
    # check if we can get an object
    product = get_object_or_404(Product, slug=slug)
    # the variable is used to display the amount of ordered products
    # get_or_create method is used not to create new objects, but to add +1 to the existing
    order_product, created = OrderProduct.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = OrderList.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the ordered item is within the order list
        if order.items.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, "The product's quantity is being updated!")
        else:
            messages.info(request, "This product is now in your shopping cart!")
            order.items.add(order_product)
    else:
        ordered_date = timezone.now()
        order = OrderList.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_product)
        messages.info(request, "This product is now in your shopping cart!")
    return redirect("order_summary")


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = OrderList.objects.filter(
        user=request.user,
        ordered=False,)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            #removes the product from the shopping cart
            order.items.remove(order_product)
            messages.info(request, "This product was removed from your shopping cart!")
            return redirect("product-detail", slug=slug)
        else:
            messages.info(request, "This product isn't in your cart")
            return redirect("product-detail", slug=slug)
    else:
        messages.info(request, "You don't have an order")
        return redirect("product-detail", slug=slug)


@login_required
def remove_one_product_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = OrderList.objects.filter(
        user=request.user,
        ordered=False,)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                #decreases the number of product by 1
                order_product.quantity -= 1
                order_product.save()
                messages.info(request, "This product quantity was updated!")
            else:
                order.items.remove(order_product)
                messages.info(request, "This product was deleted!")
            return redirect("order_summary")
        else:
            messages.info(request, "This product isn't in your cart")
            return redirect("order_summary")
    else:
        messages.info(request, "You don't have an order")
        return redirect("order_summary")


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = OrderList.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                #add the coupon to the models
                #passes the coupon form to the shopping cart
                'couponform': CouponForm()
            }
            return render(self.request, 'shop/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class Checkout(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # Check if the user has previously selected 'save_info'
            user_data = BillingAddress.objects.filter(user=self.request.user, save_info=True)
            print(user_data)
            print(type(user_data))
            if user_data.exists():
                # grab the last saved billing address
                user_initial = user_data[len(user_data) - 1]
                print(user_initial)
                # add the initial_data to form
                initial_data = {
                    'first_name': user_initial.firstname,
                    'last_name': user_initial.lastname,
                    'phone_number': user_initial.phone_number,
                    'email_address': user_initial.email_address,
                    'address': user_initial.address,
                    'zip_code': user_initial.zip_code,
                    'country': user_initial.country,
                }
                #dispays CheckoutForm
                form = CheckoutForm(initial=initial_data)
                context = {
                    'form': form
                }
                return render(self.request, 'shop/checkout.html', context)
            else:
                form = CheckoutForm()
            context = {
                'form': form
            }
            return render(self.request, 'shop/checkout.html', context)
        except ObjectDoesNotExist:
            form = CheckoutForm()
            context = {
                'form': form
            }
            return render(self.request, 'shop/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            print(self.request.POST)
            order = OrderList.objects.get(user=self.request.user, ordered=False)
            print('received')
            if form.is_valid():
                print('entered')
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email_address = form.cleaned_data['email_address']
                address = form.cleaned_data['address']
                zip_code = form.cleaned_data['zip_code']
                country = form.cleaned_data['country']
                payment_option = form.cleaned_data['payment_option']
                save_info = form.cleaned_data['save_info']
                print(save_info)
                billing_address = BillingAddress(
                    firstname=first_name,
                    lastname=last_name,
                    phone_number=phone_number,
                    email_address=email_address,
                    user=self.request.user,
                    address=address,
                    zip_code=zip_code,
                    country=country,
                    save_info=save_info,
                )
                billing_address.save()
                print('done1')
                #adds the relationship between OrderList and BillingAddress
                order.billing_address = billing_address
                order.save()
                print('done2')
                if payment_option == 'credit card':
                    print('redirecting to credit card view')
                    return redirect('credit card/', payment_option='Credit Card')
                #currently unavailable function
                elif payment_option == 'paypal':
                    messages.warning(self.request, 'Currently unavailable')
                    print('redirecting')
                    return redirect('/order_checkout/', payment_option='PayPal')
                else:
                    messages.warning(self.request, 'Please select the payment method')
                    return redirect('order_checkout/')
            else:
                messages.warning(self.request, "Something went wrong")
                return redirect('order_checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class Payment(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = OrderList.objects.get(user=self.request.user, ordered=False)
            form = PaymentForm(self.request.POST or None)
            context = {
                'form': form,
                'object': order,
            }
            return render(self.request, 'shop/payment.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an order")
            return redirect('/')

    def post(self, *args, **kwargs):
        order_product = OrderProduct.objects.filter(user=self.request.user, ordered=False)
        order = OrderList.objects.get(user=self.request.user, ordered=False)
        print(order.items.all())
        form = PaymentForm(self.request.POST or None)
        if form.is_valid():
            print('Payment Entered')
            card_name = form.cleaned_data['card_name']
            card_number = form.cleaned_data['cardnumber']
            exp_date = form.cleaned_data['exp_date']
            cvv = form.cleaned_data['cvv']
            payment_information = PaymentInformation(
                card_name=card_name,
                card_number=card_number,
                exp_date=exp_date,
                cvv=cvv,
                user=self.request.user,
                items = order,
            )
            payment_information.save()
            order.ordered=True
            order.save()
            order_product.update(ordered=True)
            for order_p in order_product:
                order_p.save()
            print('Payment Saved')
            return redirect('email/')
        else:
            messages.warning(self.request, "The card details are not correct")
            return redirect('/order_checkout/credit card/')

#sends the confirmation email to the provided email address
#can be replaced with a direct order receipt
def email(request):
    try:
        billing_address = BillingAddress.objects.filter(user=request.user).last()
        print(billing_address.address)
    except ObjectDoesNotExist:
        return redirect('/')
    subject = 'Your Recent Order with our *Company*'
    message = f'Hello {billing_address.firstname} Thank you for your purchase. Your order will soon be processed and sent to "{billing_address.address}". Thank you for your trust.'
    send_mail(subject, #str
              message, #str
              'oleg.neichev@gmail.com', #str
              #the list of emails should be replaced with billing_address.email_address
              ['oleg.neichev@gmail.com'], #list
              fail_silently=False) #bool
    return render(request, 'shop/email.html')


class CommentCreate(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CommentForm(self.request.POST or None)
        context = {
            'form': form
        }
        return render(self.request, 'shop/comment.html', context)

    def post(self, *args, **kwargs):
        try:
            slug = self.kwargs.get("slug")
            print(slug)
            product = get_object_or_404(Product, slug=slug)
            print(product)
            form = CommentForm(self.request.POST or None)
            print(self.request.POST)
            if form.is_valid():
                print('comment form is valid')
                username = form.cleaned_data['username']
                context = form.cleaned_data['context']
                positive = form.cleaned_data['positive']
                negative = form.cleaned_data['negative']
                comment = Comment(
                    username=username,
                    context=context,
                    positive=positive,
                    negative=negative,
                    user=self.request.user,
                    prod=product,
                )
                comment.save()
                product.com = comment
                product.save()
                return redirect('product-detail', slug=slug)
        except ObjectDoesNotExist:
            messages.error(self.request, 'This product does not exist')
            return redirect('/')

@login_required
def comment_like(request, slug, *args, **kwargs):
    comment = get_object_or_404(Comment, slug=slug)
    redirect_ = comment.prod
    product = Product.objects.get(title=redirect_)
    user = request.user
    if user.is_authenticated:
        #removes a client from a Product.likes model. Works only with ManyToMany Field
        if user in comment.likes.all():
            comment.likes.remove(user)
            return redirect("product-detail", slug=product.slug)
        #adds a client from a Product.likes model. Works only with ManyToMany Field
        else:
            comment.likes.add(user)
            return redirect("product-detail", slug=product.slug)
    return redirect("product-detail", slug=redirect_)

#grabs a given coupon
def get_coupon(request, coupon):
    try:
        coupon = Coupon.objects.get(coupon=coupon)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "You have no order")
        return redirect("order_summary")
    return redirect("order_summary")

#applies the coupon to the order
def apply_coupon(request):
    if request.method == "POST":
        #the form is used to validate a coupon before the assignment
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                coupon = form.cleaned_data.get("coupon")
                order = OrderList.objects.get(user = request.user, ordered=False)
                #checks if the coupon exists
                order.coupon = get_coupon(request, coupon)
                order.save()
                messages.success(request, "The code has been applied")
                return redirect("order_summary")
            except ObjectDoesNotExist:
                messages.error(request, "The coupon is invalid")
                return redirect("order_summary")
        else:
            messages.error(request, "The coupon is invalid")
            return redirect("order_summary")
    #unhandeled exception
    return None

def remove_coupon(request):
    try:
        order = OrderList.objects.get(user = request.user, ordered=False)
        #as the relationship is not ManyToMany, the object is deleted from both models
        #To set the variable to None is a workaround
        order.coupon = None
        order.save()
        messages.success(request, "The coupon has been removed")
        return redirect("order_summary")
    except ObjectDoesNotExist:
        messages.error(request, "There is no coupon attached")
        return redirect("order_summary")

#rendres the page with all the coupons
def coupon_list(request):
    coupon = Coupon.objects.all()
    return render(request, "shop/coupon.html", {'coupons': coupon})

#represents the company
def about(request):
    return render(request, "shop/about.html")
