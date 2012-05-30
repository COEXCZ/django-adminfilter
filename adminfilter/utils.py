# -*- coding: utf-8 -*-
from django.forms.forms import BoundField


class FieldStack(object):
    """ Wrapper pro skupinu policek ve formulari

    """
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def __nonzero__(self):
        return bool(self.args)

    def __get__(self, form, objtype=None):
        return FieldStackLazy(form, *self.args, **self.kwargs)
       
class FieldStackLazy(object):
    """ Lazy trida pro pristup k FieldStacku

    """
    def __init__(self, form, *args, **kwargs):
        self.form, self.args, self.kwargs = form, args, kwargs

    def __nonzero__(self):
        return bool(self.args)

    def __iter__(self):
        for field in self.args:
            if isinstance(field, (list, tuple)):
                yield [BoundField(self.form, self.form.fields[f], f) for f in field]
            else:
                yield BoundField(self.form, self.form.fields[field], field)

    def __getattr__(self, name):
        try:
            return self.kwargs[name]
        except KeyError, e:
            raise AttributeError(e)

    def copy(self, title=None):
        kwargs = self.kwargs.copy()
        if not title is None:
            kwargs['title'] = title
        return FieldStack(*self.args, **kwargs)
