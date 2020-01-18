from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Coupon
import re


def valid_card_number(value):
    print('Checking the card number')
    #checks if the card contains only digits
    if value.isnumeric():
        #validates the card.
        pattern = re.compile(r'([0-9]{4}){4}')
        matcher = pattern.match(value)
        if matcher:
            print('Success')
            return value
        else:
            print("Credit card failed")
            raise forms.ValidationError("The card number is not valid")
    else:
        raise forms.ValidationError(_('Invalid value'), code='invalid')

#checks if the Coupon model has a provided coupon
def valid_coupon(value):
    try:
        coupon = Coupon.objects.get(coupon=value)
        return value
    except Exception:
        raise forms.ValidationError("The coupon is invalid")

    raise forms.ValidationError("The coupon is invalid")

#simple check for any variable that should be numeric
def numeric(value):
    if value.isnumeric():
        return value
    else:
        raise forms.ValidationError(_('Invalid value'), code='invalid')
