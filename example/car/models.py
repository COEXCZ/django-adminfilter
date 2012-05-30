# -*- coding: utf-8 -*-
from django.db import models

from choices import BRANDS, COLORS, FUEL_TYPES


class Car(models.Model):
    name = models.CharField(max_length=180)
    brand = models.CharField(max_length=80, choices=BRANDS)

    price = models.IntegerField(help_text='USD')

    model_year = models.IntegerField(blank=True, null=True)
    kms_done = models.IntegerField(blank=True, null=True)
    crashed = models.BooleanField(default=False)

    color = models.CharField(max_length=80, choices=COLORS, blank=True)
    interior_color = models.CharField(max_length=80, choices=COLORS, blank=True)
    fuel_type = models.CharField(max_length=80, choices=FUEL_TYPES, blank=True)
    doors = models.IntegerField(blank=True, null=True)

    notes = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.get_brand_display(), self.name)
