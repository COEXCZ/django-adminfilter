# -*- coding: utf-8 -*-
from django.conf import settings

def global_vars(request):
    return {"ENABLE_GA_TRACKING": settings.ENABLE_GA_TRACKING}
