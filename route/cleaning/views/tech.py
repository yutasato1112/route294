from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings

class techView(TemplateView):
    template_name = "tech.html"
    def get(self, request, *args, **kwargs):
        context = {
            'app_version': getattr(settings, 'APP_VERSION', ''),
        }
        return render(self.request, self.template_name, context)