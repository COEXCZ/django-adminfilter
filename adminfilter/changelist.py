# -*- coding: utf-8 -*-

from django.contrib.admin.views.main import ChangeList, ORDER_VAR, ORDER_TYPE_VAR
from django.contrib.admin.util import quote
from django.core.paginator import Paginator, InvalidPage
from django.utils.http import urlencode

from choices import ITEMS_PER_PAGE_CONST


FILTER_PREFIX = 'cl'
LIST_PER_PAGE_VAR = u'll'
PAGE_VAR = 'p'


def prefix_cl_param(p):
    return u'%s-%s' % (FILTER_PREFIX, p)


class FilterChangeList(ChangeList):
    """ Extended Django admin changelist for advanced custom filters

    """
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin):
        self.request = request
        self._filter_form = None

        super(FilterChangeList, self).__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin)

        # Ordering parameter override to 'cl'
        if prefix_cl_param(ORDER_VAR) in self.params:
            self.params[ORDER_VAR] = self.params[prefix_cl_param(ORDER_VAR)]
        if prefix_cl_param(ORDER_VAR) in self.params:
            self.params[ORDER_TYPE_VAR] = self.params[prefix_cl_param(ORDER_TYPE_VAR)]
        self.order_field, self.order_type = self.get_ordering()

        # Paginator
        try:
            self.list_per_page = int(self.filter_form.cleaned_data.get(LIST_PER_PAGE_VAR, ITEMS_PER_PAGE_CONST))
        except ValueError:
            self.list_per_page = ITEMS_PER_PAGE_CONST

        try:
            self.page_num = int(self.filter_form.cleaned_data.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0

        self.paginator = Paginator(self.get_query_set(), self.list_per_page)
        self.result_count = self.paginator.count

        if self.filter_form.cleaned_data.get(LIST_PER_PAGE_VAR) == -1:
            self.result_list = self.query_set._clone()
        else:
            try:
                self.result_list = self.paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                self.result_list = ()

    @property
    def filter_form(self):
        """ Filter form initialization. It uses model_admin definition of
            custom filter_form.

        """
        if self._filter_form is None:
            self._filter_form = self.model_admin.filter_form(self.request.REQUEST)
            self._filter_form.is_valid()

        return self._filter_form

    def get_query_set(self):
        """ Returns queryset objects for change list

            Additional class info:
                self.query_set = self.get_query_set()

        """
        # self.filter_form.queryset calls S's instance __get__ method with paramater self.root_query_set
        qs = self.filter_form.queryset(self.root_query_set) if hasattr(self.filter_form, 'queryset') else self.root_query_set

        # Set ordering - hack for compatibility with MPTTChangeList
        if getattr(self.model_admin, 'use_mptt', False):
            # always order by (tree_id, left)
            tree_id = qs.model._mptt_meta.tree_id_attr
            left = qs.model._mptt_meta.left_attr
            qs = qs.order_by(tree_id, left)

        else:
            if self.order_field:
                qs = qs.order_by('%s%s' % ((self.order_type == 'desc' and '-' or ''), self.order_field))

        return qs.distinct()

    def get_query_string(self, new_params=None, remove=None):
        """
        Overriden method. Extend or remove params of changelist and return resulting query string.
        """
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []

        p = self.filter_form.cleaned_data_prefixed

        for r in remove:
            for k in p.keys():
                if (k).startswith(prefix_cl_param(r)):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if prefix_cl_param(k) in p:
                    del p[prefix_cl_param(k)]
            else:
                p[prefix_cl_param(k)] = v
        return '?%s' % urlencode(p)

    def url_for_result(self, result):
        """
        Contruct change URL for result item.
        """
        return "%s/?%s" % (quote(getattr(result, self.pk_attname)), self.request.META.get('QUERY_STRING', ''))
