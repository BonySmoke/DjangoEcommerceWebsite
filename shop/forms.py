from django import forms
from django_countries.fields import CountryField
from .validators import valid_card_number, valid_coupon, numeric
from .models import PaymentInformation, Comment

PAYMENT_OPTION = [
    ('credit card', 'Credit Card'),
    ('paypal', 'PayPal')
]


class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'checkout_input'}))
    last_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Your Last Name', 'class': 'checkout_input'}))
    phone_number = forms.CharField(required=True,
                                   validators=[numeric], widget=forms.TextInput(attrs={'placeholder': 'Your Phone number', 'class': 'checkout_input'}))
    email_address = forms.EmailField(required=True,
                                     widget=forms.TextInput(attrs={'placeholder': 'Your email_address', 'class': 'checkout_input'}))
    address = forms.CharField(required=True,
                              widget=forms.TextInput(attrs={'placeholder': 'Where to send the order', 'class': 'checkout_input'}))
    zip_code = forms.CharField(validators=[numeric], required=True, max_length=6, widget=forms.TextInput(attrs={'class': 'checkout_input'}))
    save_info = forms.BooleanField(required=False)
    country = CountryField(blank_label='select country').formfield()
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_OPTION)


class PaymentForm(forms.ModelForm):
    card_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'checkout_input'}))
    cardnumber = forms.CharField(validators=[valid_card_number], min_length=12, max_length=16, widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000', 'class': 'checkout_input'}))
    exp_date = forms.DateInput(attrs={'type': 'date', 'class': 'checkout_input'})
    cvv = forms.CharField(required=True, max_length=4, min_length=3, widget=forms.TextInput(attrs={'class': 'checkout_input'}))

    class Meta:
        model = PaymentInformation
        fields = ['card_name', 'cardnumber', 'exp_date', 'cvv']
        # creates a beautiful html calender
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'id': 'exampleFormControlInput1'}))
    context = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'id':'exampleFormControlTextarea1', 'rows':8}))
    positive = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'id':'exampleFormControlTextarea1', 'rows':8}))
    negative = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'id':'exampleFormControlTextarea1', 'rows':8}))

    class Meta:
        model = Comment
        fields = ['username', 'context', 'positive', 'negative']

class CouponForm(forms.Form):
    coupon = forms.CharField(validators=[valid_coupon], max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Enter the coupon'}))
