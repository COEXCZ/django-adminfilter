# -*- coding: utf-8 -*-
from copy import deepcopy

from django import forms
from django.conf import settings
from django.core import urlresolvers
from django.db.models import Q, Model
from django.forms.forms import BoundField
from django.forms.util import ErrorDict
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

import choices
from changelist import FILTER_PREFIX, LIST_PER_PAGE_VAR, PAGE_VAR
from fields import *
from utils import FieldStackLazy


__all__ = (
    'And',
    'FilterForm',
)


class S(object):
    """ Queryset contructor. Returns queryset according to custom form queryset
        definition. """

    AND = '&'
    INVALID = (u'', None)

    def __init__(self, operator, *children, **opts):
        self.operator = operator
        self.children = children
        self.lazy_init = opts.get('lazy_init', False)

    def __and__(self, other):
        return S(self.AND, self, other)

    def __or__(self, other):
        return S(self.OR, self, other)

    def __invert__(self):
        return S(self.NOT, self)

    def __get__(self, form, formtype=None):
        """ Using descriptor protocol to access data

            returns:
                get_queryset -- function

        """

        # Get field attribute names known as children and set all fields to optional
        if self.lazy_init:
            children = []
            ignore_fields = (LIST_PER_PAGE_VAR, PAGE_VAR)
            for field_name, field in form.fields.iteritems():
                if hasattr(field, 'q') and field_name not in ignore_fields:
                    children.append(field_name)
                if isinstance(field, forms.DateField):
                    field.widget.attrs = {'class': 'vDateField'}  # Grappelli class
                    field.input_formats = choices.DATE_INPUT_FORMAT
                field.required = False
            self.children = children

        def get_queryset(queryset):
            """ Accepts queryset and returns filtered queryset by form data

            """
            #order_by = []

            for field_name, field in form.fields.iteritems():
                field.value = form.cleaned_data.get(field_name)

                if self.is_valid(field.value):
                    if isinstance(field.value, basestring):
                        field.value = field.value.strip()

                    if isinstance(field.value, Model):
                        field.value = field.value.pk

                    #if getattr(field, 'order_by', None):
                        #order_by.append(field.value)

            q = self.get_combined_q(form)
            queryset = queryset.filter(q)

            fulltext_query = self.get_fulltext_query(form)
            if fulltext_query:
                queryset = queryset.fulltext(
                    fulltext_query, rank_alias='fulltext_rank'
                ).order_by('-fulltext_rank')

            #queryset = queryset.order_by(*order_by)
            return queryset

        return get_queryset

    def get_combined_q(self, form):
        """ Returns final combinad Q object for filtering

        """
        q = None

        for child in self.children:
            if not q:
                q = self.get_q(form, child)
            q = self.combine_q(form, child, q)

        return q

    def combine_q(self, form, child, q):
        """ Combines Q objects together according to self.operator

        """
        return {self.AND: q & self.get_q(form, child)}[self.operator]

    def is_valid(self, value):
        return value not in self.INVALID

    def get_q(self, form, child):
        """ Returns Q object from field in child instance

        """
        if isinstance(child, S):
            return child(form)
        else:
            child_field = form.fields[child]
            if self.is_valid(child_field.value):
                if isinstance(child_field, forms.BooleanField) and not child_field.value:
                    return Q()

                if getattr(child_field, 'fulltext', False):
                    return Q()

                if getattr(child_field, 'takes_cleaned_data', False):
                    return child_field.q(child_field.value, form.cleaned_data)
                else:
                    return child_field.q(child_field.value)

        # Last fallback
        return Q()

    def get_fulltext_query(self, form):
        """ Returns fulltext's form field query if exists """
        query = u''
        for child in self.children:
            if getattr(form.fields[child], 'fulltext', False):
                query = form.fields[child].value

        return query


def And(*children, **opts):
    return S(S.AND, *children, **opts)


class FilterForm(forms.Form):
    """ Main filter form used for inheritance and field definition.

    """

    FIELDS_TEMPLATE = "tags/filter.html"

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = FILTER_PREFIX
        super(FilterForm, self).__init__(*args, **kwargs)

        # Paginator page listing
        self.fields[PAGE_VAR] = forms.IntegerField(initial=1, widget=forms.HiddenInput, label=u'Page')

        # Items per page
        self.fields[LIST_PER_PAGE_VAR] = forms.IntegerField(
            initial=30,
            label=_(u'Per page'),
            widget=forms.Select(choices=choices.ITEMS_PER_PAGE)
            )

        self.fields['ot'] = forms.CharField(required=False, widget=forms.HiddenInput)
        self.fields['o'] = forms.IntegerField(required=False, widget=forms.HiddenInput)

        # Initialize form queryset
        if not hasattr(self.__class__, 'queryset'):
            self.__class__.queryset = And(lazy_init=True)

    def visible_filter_fields(self):
        """
        Iterator over filter form field. Per page field + current page field are iterated as last.
        """
        end_fields = []
        for bf in self.visible_fields():
            if bf.name in (LIST_PER_PAGE_VAR, PAGE_VAR):
                end_fields.append(bf)
            else:
                yield bf
        for bf in end_fields:
            yield bf

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = ErrorDict()
        if not self.is_bound:
            return
        self.cleaned_data = {}

        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def is_valid(self):
        """ ignores form errors

        """
        self._get_errors()
        return self.is_bound

    def clean(self):
        self.cleaned_data = super(FilterForm, self).clean()

        if hasattr(self, 'ignore_if'):
            for field, ignore_fields in self.ignore_if.iteritems():
                if field in self.cleaned_data and self.cleaned_data[field]:
                    for ignore_field in ignore_fields:
                        try:
                            del(self.cleaned_data[ignore_field])
                        except KeyError:
                            pass

        invalid_keys = []
        for key, value in self.cleaned_data.iteritems():
            if value in (None, u'', ''):
                invalid_keys.append(key)

        for key in invalid_keys:
            del(self.cleaned_data[key])

        return self.cleaned_data

    @property
    def cleaned_data_prefixed(self):
        d = {}

        for key, value in self.cleaned_data.iteritems():
            if isinstance(value, Model):
                value = value.pk
            d[self.add_prefix(key)] = value

        return d

    @property
    def hidden_form(self):
        """ Returns SearchForm with hidden fields

        """
        form = deepcopy(self)

        for field in form.fields.itervalues():
            field.widget = forms.HiddenInput()

        form.all_fields = FieldStackLazy(form, *form.fields.keys())
        return form

    def __getitem__(self, name):
        "Returns a BoundField with the given name."

        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)

        return BoundField(self, field, name)


class SearchData(object):
    """ holder object for filter_params and filter_form """
    pass


class LazyFilter(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_search'):
            Form = None
            request._cached_search = SearchData()

            # TODO constant to configure
            data = {
                # 'cl-ll': choices.ITEMS_PER_PAGE_CONST
            }

            # Get Admin instance
            urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
            urlresolvers.set_urlconf(urlconf)
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

            callback, callback_args, callback_kwargs = resolver.resolve(
                    request.path_info)
            admin = callback.func_closure[0].cell_contents

            if admin:
                Form = admin.filter_form
            else:
                Form = None

            if Form:
                data.update(dict(request.REQUEST))

                form = Form(data)
                form.is_valid()

                request._cached_search.filter_params = urlencode(form.cleaned_data_prefixed)
                request._cached_search.filter_form = form

        return request._cached_search
