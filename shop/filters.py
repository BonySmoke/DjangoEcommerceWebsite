import django_filters
from .models import Product
from django import forms


class SearchFilter(django_filters.FilterSet):

    #adds a search box. Returns a queryset of products that contain the input
    title = django_filters.CharFilter(label='', lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'search_line', 'placeholder': 'Type to search', 'onfocus': ''}))

    #finds the products in range between min - max
    price = django_filters.RangeFilter(label='')


    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending'),
    )

    # filter a queryset by price
    price_filter = django_filters.ChoiceFilter(label="", choices=CHOICES, method='filter_by')

    def filter_by(self, queryset, name, value):
        if value == 'ascending':
            expression = 'price'
        elif value == 'descending':
            expression = '-price'
        else:
            expression = '-available'

        return queryset.order_by(expression)

    class Meta:
        model = Product
        fields = ['title']

