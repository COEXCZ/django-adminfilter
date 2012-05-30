# -*- coding: utf-8 -*-
from itertools import groupby

from django import forms
from django.db.models import Q

from mptt import forms as mptt_forms


__all__ = (
    'CharField',
    'IntegerField',
    'ChoiceField',
    'BooleanField',
    'DateField',
    'TypedChoiceField',
    'ModelChoiceField',
    'GroupedModelChoiceField',
    'GroupedTreeModelChoiceField',
    'TreeNodeChoiceField',
    'GroupedTreeNodeModelChoiceField',
)


def filter_field(name, bases, attrs):
    """ Metaclass for wrapping form field

        Replaces original constructor
    """
    Field = type(name, bases, attrs)

    def init(self, q=None, takes_cleaned_data=False, fulltext=False, *args, **kwargs):
        """ New init function supports new arguments:

            q = lookup string or callable accepting value and returning Q object
            takes_cleaned_data = custom query then accepts second paramater cleaned_data
            fulltext =

        """

        self.takes_cleaned_data = takes_cleaned_data
        self.q = q
        self.fulltext = fulltext

        if not callable(self.q):
            self.q = lambda value: Q(**{q: value})

        if not 'required' in kwargs:
            kwargs['required'] = False

        super(Field, self).__init__(*args, **kwargs)

    setattr(Field, '__init__', init)
    return Field


class CharField(forms.CharField):
    __metaclass__ = filter_field


class IntegerField(forms.IntegerField):
    __metaclass__ = filter_field


class ChoiceField(forms.ChoiceField):
    __metaclass__ = filter_field


class TypedChoiceField(forms.TypedChoiceField):
    __metaclass__ = filter_field


class BooleanField(forms.BooleanField):
    __metaclass__ = filter_field


class DateField(forms.DateField):
    __metaclass__ = filter_field


class ModelChoiceField(forms.ModelChoiceField):
    __metaclass__ = filter_field


class TreeNodeChoiceField(mptt_forms.TreeNodeChoiceField):
    __metaclass__ = filter_field


class GroupedModelChoiceIterator(forms.models.ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield (u"", self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    (self.field.group_label(group), [self.choice(ch) for ch in choices])
                        for group, choices in groupby(self.queryset.all().select_related(),
                            key=lambda row: getattr(row, self.field.group_by_field))
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for group, choices in groupby(self.queryset.all().select_related(),
                    key=lambda row: getattr(row, self.field.group_by_field)):
                yield (self.field.group_label(group), [self.choice(ch) for ch in choices])


class GroupedTreeModelChoiceField(mptt_forms.TreeNodeChoiceField):
    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        group_by_field is the name of a field on the model
        group_label is a function to return a label for each choice group
        """
        super(GroupedTreeModelChoiceField, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        """
        Exactly as per ModelChoiceField except returns new iterator class
        """
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


class BaseGroupedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        group_by_field is the name of a field on the model
        group_label is a function to return a label for each choice group
        """
        super(BaseGroupedModelChoiceField, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        """
        Exactly as per ModelChoiceField except returns new iterator class
        """
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


class GroupedTreeNodeModelChoiceField(GroupedTreeModelChoiceField):
    __metaclass__ = filter_field


class GroupedModelChoiceField(BaseGroupedModelChoiceField):
    __metaclass__ = filter_field
