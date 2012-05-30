# -*- coding: utf-8 -*-
from forms import LazyFilter


class FilterMiddleware(object):
    def process_request(self, request):
        # Class attribute filter
        request.__class__.filter = LazyFilter()
