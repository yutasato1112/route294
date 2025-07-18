from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime
import json
from django.http import JsonResponse
from urllib.parse import urlparse

from ..utils.home_util import read_csv, processing_list, dist_room, room_person, room_char

# Create your views here.

class homeView(TemplateView):
    template_name = "home.html"
    
    def get(self, request, *args, **kwargs):
        method = 'GET'
        
        #遷移前取得
        referer = request.META.get('HTTP_REFERER')  
        from_report = False  
        form_ai = False
        if referer:
            # URLのパス部分だけ取り出す
            path = urlparse(referer).path
            if path.endswith('/report/') or path == '/report':
                from_report = True
            if path.endswith('/ai_assist/') or path == '/ai_assist':
                from_ai = True

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
        #起動時刻が18時から24時の場合、翌日の日付を表示
        #それ以外は当日の日付を表示
        if datetime.datetime.now().hour >= 18:
            today = datetime.date.today() + datetime.timedelta(days=1)
        else:
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
            'remarks_len':3,
            'add_remarks_len':0,
            'room_changes_len':3,
            'outins_len':3,
            'must_cleans_len':3,
            'add_contacts_len':0,
            'contacts_len':3,
            'from_report': from_report,
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
        room_changes = data['room_changes']
        outins = data['outins']
        must_cleans = data['must_cleans']
        others = data['others']
        contacts = data['contacts']
        is_drain_water = data.get('is_drain_water', False)
        is_highskite = data.get('is_highskite', False)
        is_chlorine = data.get('is_chlorine', False)
        is_chemical_clean = data.get('is_chemical_clean', False)
        is_public = data.get('is_public', False)
        
        
        #備考の欄数
        if len(remarks) < 3:
            remarks_len = 3-len(remarks)
        else:
            remarks_len=1
        
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
        
        #大浴場追加要員
        original_add_bath = data['add_bath']
        add_bath = []
        for i in original_add_bath:
            if i != '':
                add_bath.append(i)
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
            'combined_rooms': combined_rooms,
            'editor_name': editor_name,
            'bath_persons': bath_persons,
            'remarks': remarks,
            'house_person': house_person,
            'eco_rooms': eco_rooms,
            'ame_rooms': ame_rooms,
            'duvet_rooms': duvet_rooms,
            'house_len': house_len,
            'add_house_len':len(house_person),
            'room_char_list':room_char_list,
            'room_char_list_len':room_char_list_len,
            'remarks_len':remarks_len,
            'add_remarks_len':len(remarks),
            'room_changes_len':len(room_changes)+1,
            'outins_len':len(outins)+1,
            'must_cleans_len':len(must_cleans)+1,
            'room_changes':room_changes,
            'outins':outins,
            'must_cleans':must_cleans,
            'others':others,
            'add_bath':add_bath,
            'contacts': contacts,
            'add_contacts_len':len(contacts),
            'contacts_len':len(contacts)+3,
            'from_report': False,
            'is_drain_water': is_drain_water,
            'is_highskite': is_highskite,
            'is_chlorine': is_chlorine,
            'is_chemical_clean': is_chemical_clean,
            'is_public': is_public,
        }
        return render(self.request, self.template_name, context)
