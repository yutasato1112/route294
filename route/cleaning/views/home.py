from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime
import json
from django.http import JsonResponse

from ..utils.home_util import read_csv, processing_list, dist_room, room_person, room_char

# Create your views here.

class homeView(TemplateView):
    template_name = "home.html"
    
    def get(self, request, *args, **kwargs):
        method = 'GET'
        #初回アクセス時
        #csv読み込み
        room_info_data, times_by_time_data, master_key_data = read_csv()
        
        #部屋を階別に二次元配列へ加工
        room_num_table = processing_list(room_info_data)
        
        #部屋をタイプ別に一次元配列に加工
        single_room_list, twin_room_list = dist_room(room_info_data)
        combined_rooms = []
        for i in range(len(room_num_table)):
            floor_data = []
            for j in range(len(room_num_table[i])):
                floor_data.append({
                    'room': room_num_table[i][j],
                    'status': '',
                })
            combined_rooms.append(floor_data)


        #日付取得
        today = datetime.date.today()
        
        context = {
            'method':method,
            'single_time':int(times_by_time_data[0][1]),
            'twin_time':int(times_by_time_data[1][1]),
            'bath_time':int(times_by_time_data[2][1]),
            'today':today,
            'rooms':room_num_table,
            'combined_rooms': combined_rooms,
            'master_key':master_key_data,
            'single_rooms':single_room_list,
            'twin_rooms':twin_room_list,
            'house_len':10,
            'room_char_list_len':10,
        }
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        method = 'POST'
        json_file = request.FILES['json_file']
        try:
            data = json.load(json_file)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'json read failed'}, status=400)

        #csv読み込み
        room_info_data, times_by_time_data, master_key_data = read_csv()
        
        #部屋を階別に二次元配列へ加工
        room_num_table = processing_list(room_info_data)
        
        #部屋をタイプ別に一次元配列に加工
        single_room_list, twin_room_list = dist_room(room_info_data)

        #編集情報の取得
        editor_name = data['editor_name']
        date_str = data['date']
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        single_time = int(data['single_time'])
        twin_time = int(data['twin_time'])
        bath_time = int(data['bath_time'])
        room_inputs = data['room_inputs']
        bath_persons = data['bath_person']
        remarks = data['remarks']
        house_person = data['house_data']
        eco_rooms = data['eco_rooms']
        ame_rooms = data['ame_rooms']
        duvet_rooms = data['duvet_rooms']
        
        #部屋の清掃担当リストを加工
        combined_rooms = room_person(room_num_table, room_inputs)
        if len(house_person) < 10:
            house_len = 10-len(house_person)
        else:
            house_len = 1
            
        #エコ・アメ・デュべ部屋の処理
        room_char_list = room_char(eco_rooms, ame_rooms, duvet_rooms)
        if len(room_char_list) < 10:
            room_char_list_len = 10-len(house_person)
        else:
            room_char_list_len = 1

        context = {
            'method':method,
            'single_time':single_time,
            'twin_time':twin_time,
            'bath_time':bath_time,
            'today':date,
            'master_key':master_key_data,
            'single_rooms':single_room_list,
            'twin_rooms':twin_room_list,
            'rooms':room_num_table,
            'room_person':room_person,
            'combined_rooms': combined_rooms,
            'editor_name': editor_name,
            'bath_persons': bath_persons,
            'remarks': remarks,
            'house_person': house_person,
            'eco_rooms': eco_rooms,
            'ame_rooms': ame_rooms,
            'duvet_rooms': duvet_rooms,
            'house_len': house_len,
            'room_char_list':room_char_list,
            'room_char_list_len':room_char_list_len,
        }
        return render(self.request, self.template_name, context)
