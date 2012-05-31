# -*- coding: utf-8 -*-
from django.shortcuts import render


def homepage(request):
    returen render(request, 'homepage.html')
