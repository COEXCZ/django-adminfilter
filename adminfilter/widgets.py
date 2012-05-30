# -*- coding: utf-8 -*-
from django.forms import widgets


def add_class(widget, css_class, title=None):
    """
    Helper function - adds CSS class or title to widget
    """
    attrs = widget.attrs or {}
    if 'class' in attrs:
        attrs['class'] = u'%s %s' % (attrs['class'], css_class)
    else:
        attrs['class'] = css_class

    if title:
        if 'title' in attrs:
            attrs['title'] = u'%s %s' % (attrs['title'], title)
        else:
            attrs['title'] = title

    widget.attrs = attrs

class PaginatorInput(widgets.TextInput):
    """ Text input for paginator - defaults to value "1"

    """
    def render(self, name, value, attrs=None):
        return super(PaginatorInput, self).render(name, value if value else 1, attrs)
