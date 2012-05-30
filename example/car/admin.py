# -*- coding: utf-8 -*-
from django.contrib import admin

from adminfilter import FilterAdmin

from models import Car
from forms import CarFilterForm


class CarAdmin(FilterAdmin):
    filter_form = CarFilterForm
    list_display = (
        'name',
        'brand',
        'price',
        'color',
        'model_year',
        'kms_done',
        'crashed',
        'fuel_type',
        'doors',
    )


admin.site.register(Car, CarAdmin)
