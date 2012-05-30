# -*- coding: utf-8 -*-
from django.db.models import Q


def price_from_q(value):
    if value:
        return Q(price__gte=value)
    else:
        return Q()


def price_to_q(value):
    if value:
        return Q(price__lte=value)
    else:
        return Q()
