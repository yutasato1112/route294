from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from ..utils.preview_util import catch_post

# Create your views here.

class previewView(TemplateView):
    template_name = "preview.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        #データ受け取り
        date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms = catch_post(request)
                 
                    
        context = {
            'date': date,
            'single_time': single_time,
            'twin_time': twin_time,
            'bath_time': bath_time,
            'room_inputs': room_inputs,
            'bath_person': bath_person,
            'remarks': remarks,
            'house_data': house_data,
            'eco_rooms': eco_rooms,
            'ame_rooms': ame_rooms,
            'duvet_rooms': duvet_rooms,
        }
        return render(self.request, self.template_name, context)
