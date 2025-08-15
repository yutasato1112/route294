from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime
import json
from django.http import JsonResponse
from urllib.parse import urlparse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

@method_decorator(staff_member_required, name='dispatch') 
class administratorView(TemplateView):
    template_name = "administrator.html"
    def administrator(request):
        return render(request, "administrator.html")