# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from forms import FilterForm
from changelist import FilterChangeList


__all__ = ('FilterAdmin', )



change_list_template = 'filter_change_list.html'


def get_changelist(self, request, **kwargs):
    return FilterChangeList

def response_add(self, request, obj, post_url_continue='../%s/'):
    """ Customized response_add without popup redirects

    """
    opts = obj._meta
    pk_value = obj._get_pk_val()

    msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
    if "_continue" in request.POST:
        self.message_user(request, msg + ' ' + _("You may edit it again below."))
        post_url_continue += "?%s" % request.filter.filter_params
        return HttpResponseRedirect(post_url_continue % pk_value)

    if "_addanother" in request.POST:
        self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
        return HttpResponseRedirect(request.path + "?%s" % request.filter.filter_params)
    else:
        self.message_user(request, msg)

        # Figure out where to redirect. If the user has change permission,
        # redirect to the change-list page for this object. Otherwise,
        # redirect to the admin index.
        if self.has_change_permission(request, None):
            post_url = '../?%s' % request.filter.filter_params
        else:
            post_url = '../../../?%s' % request.filter.filter_params
        return HttpResponseRedirect(post_url)

def response_change(self, request, obj):
    """
    Customized response_change without popup redirects
    """
    opts = obj._meta

    verbose_name = opts.verbose_name
    if obj._deferred:
        opts_ = opts.proxy_for_model._meta
        verbose_name = opts_.verbose_name

    pk_value = obj._get_pk_val()

    msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}
    if "_continue" in request.POST:
        self.message_user(request, msg + ' ' + _("You may edit it again below."))
        return HttpResponseRedirect(request.path + '?%s' % request.filter.filter_params)
    elif "_saveasnew" in request.POST:
        msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % {'name': force_unicode(verbose_name), 'obj': obj}
        self.message_user(request, msg)
        return HttpResponseRedirect("../%s/?%s" % (pk_value, request.filter.filter_params))
    elif "_addanother" in request.POST:
        self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(verbose_name)))
        return HttpResponseRedirect("../add/?%s" % request.filter.filter_params)
    else:
        self.message_user(request, msg)
        if self.has_change_permission(request, None):
            return HttpResponseRedirect('../?%s' % request.filter.filter_params)
        else:
            return HttpResponseRedirect('../../../?%s' % request.filter.filter_params)

def filteradmin_factory(BaseClass):
    """ Creates FilterAdmin class inherited from BaseClass parameter

    Keyword parameters:
        BaseClass -- class instance

    Returns:
        Filter Admin Class - <class '__main__.Filter' + BaseClass.__name__>

    """
    attrs = {
        'change_list_template': change_list_template,
        'get_changelist': get_changelist,
        'response_add': response_add,
        'response_change': response_change,
    }
    return type('Filter' + BaseClass.__name__, (BaseClass,), attrs)


FilterAdmin = filteradmin_factory(admin.ModelAdmin)
