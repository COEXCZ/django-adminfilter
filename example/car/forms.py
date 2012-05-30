# -*- coding: utf-8 -*-
from django.db.models.fields import BLANK_CHOICE_DASH

from project.modules import adminfilter

from choices import BRANDS, COLORS, FUEL_TYPES
import query

class CarFilterForm(adminfilter.FilterForm):
    """ Car FilterForm for admin """

    brand = adminfilter.ChoiceField(q='brand', choices=tuple(BLANK_CHOICE_DASH) + BRANDS)
    color = adminfilter.ChoiceField(q='color', choices=tuple(BLANK_CHOICE_DASH) + COLORS)
    interior_color = adminfilter.ChoiceField(q='color', choices=tuple(BLANK_CHOICE_DASH) + COLORS)
    fuel_type = adminfilter.ChoiceField(q='color', choices=tuple(BLANK_CHOICE_DASH) + FUEL_TYPES)
    crashed = adminfilter.BooleanField(q='crashed')
    doors = adminfilter.IntegerField(q='doors')

    price_from = adminfilter.IntegerField(q=query.price_from_q)
    price_to = adminfilter.IntegerField(q=query.price_to_q)
