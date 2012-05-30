# -*- coding: utf-8 -*-
import math

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def filter_form(context):
    """
        @return html container with admin filter fields
    """
    form = context['cl'].filter_form
    return render_to_string(form.FIELDS_TEMPLATE, {"form": form})


@register.filter
def humanized_ul(array, columns):
    """ Split iterable object to desired number of arrays according to columns

        returns:
            list -- list with lists
    """
    array = list(array)
    if len(array):
        def list_chunks(l, num_of_items_in_column):
            for i in range(0, len(l), num_of_items_in_column):
                yield l[i:i + num_of_items_in_column]

        num_of_items_in_column = int(math.ceil(len(array) / float(columns)))
        return list(list_chunks(array, num_of_items_in_column))
    else:
        return array
