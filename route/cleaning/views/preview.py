from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from ..utils.preview_util import catch_post, is_bath, weekly_cleaning,calc_room, calc_end_time, changeDate

# Create your views here.

class previewView(TemplateView):
    template_name = "preview.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        #データ受け取り
        date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name = catch_post(request)

        #パーソン人数
        person_count = len(house_data)
        
        total_data = []
        #パーソンごとにデータを整理
        for i in range(person_count):
            name = house_data[i][1]
            key = house_data[i][2]
            bath = is_bath(bath_person, i+1)
            weekly = weekly_cleaning(date)
            room, floor = calc_room(room_inputs, eco_rooms, duvet_rooms, remarks, i+1, single_rooms, twin_rooms)
            time_of_end = calc_end_time(single_time, twin_time, bath_time, bath, room, single_rooms, twin_rooms)
            date_jp = changeDate(date)
            
            persons_cleaning_data = {
                'name':name,
                'rooms':room,
                'bath':bath,
                'key':key,
                'weekly':weekly,
                'end_time':time_of_end,
                'date':date_jp,
                'floor':floor,
            }
            total_data.append(persons_cleaning_data)
        context = {
            'data':total_data,
            'editor_name': editor_name,
        }
        return render(self.request, self.template_name, context)
