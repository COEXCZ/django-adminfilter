# -*- coding: utf-8 -*-


def filter_context_processor(request):
    """ Fills up variables filter_params, filter_form_hidden.

    """
    if hasattr(request, 'filter'):
        return vars(request.filter)
    else:
        return {}
