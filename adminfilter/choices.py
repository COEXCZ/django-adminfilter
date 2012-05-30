# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _


ALL = _(u'All')

ITEMS_PER_PAGE = (
    (-1, ALL),
    (30, 30),
    (50, 50),
    (100, 100)
)

ITEMS_PER_PAGE_CONST = 20

DATE_INPUT_FORMAT = ('%d.%m.%Y', '%Y-%m-%d')
