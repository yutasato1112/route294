from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime
import json
from django.http import JsonResponse
from urllib.parse import urlparse
from ..utils.home_util import read_csv, processing_list, dist_room, room_person, room_char
from ..utils.ai_util import get_data, processing_input_rooms,get_post_data

import openai
import os
# Create your views here.

class aiAssistView(TemplateView):
    template_name = "ai_assist.html"
    res_template_name = "ai_assist_result.html"
    def get(self, request, *args, **kwargs):
        method = 'GET'
        from_report = False  

        #csv読み込み
        room_info_data, times_by_time_data, master_key_data = read_csv()
        
        #部屋を階別に二次元配列へ加工
        room_num_table = processing_list(room_info_data)
        
        #部屋をタイプ別に一次元配列に加工
        single_room_list, twin_room_list = dist_room(room_info_data)
        
        #引渡しデータ取得
        data = get_data(request)
        editor_name = data['editor_name']
        date_str = data['date']
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        single_time = int(data['single_time'])
        twin_time = int(data['twin_time'])
        bath_time = int(data['bath_time'])
        room_inputs = data['room_inputs']
        bath_persons = data['bath_person']
        house_person = data['house_data']
        eco_rooms = data['eco_rooms']
        ame_rooms = data['ame_rooms']
        duvet_rooms = data['duvet_rooms']
        
        proc_room_inputs = processing_input_rooms(room_inputs)
        
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
            'editor_name':editor_name,
            'date':date,
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
            'house_person': house_person,
            'eco_rooms': eco_rooms,
            'ame_rooms': ame_rooms,
            'duvet_rooms': duvet_rooms,
            'house_len': house_len,
            'add_house_len':len(house_person),
            'room_char_list':room_char_list,
            'room_char_list_len':room_char_list_len,
            'from_report': False,
        }
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #日付取得
        #起動時刻が18時から24時の場合、翌日の日付を表示
        #それ以外は当日の日付を表示
        if datetime.datetime.now().hour >= 18:
            today = datetime.date.today() + datetime.timedelta(days=1)
        else:
            today = datetime.date.today()
            
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

        #送信データ取得
        data = request.POST
        house_no = data.getlist('no')
        house_name = data.getlist('name')
        house_max = data.getlist('max')
        house_least_floor = data.getlist('least_floor')
        house_is_least_comfort = data.getlist('is_least_comfort')
        house_is_bath = data.getlist('is_bath')
        
        eco_rooms = data.getlist('eco_room')
        eco_rooms = [x for x in eco_rooms if x]  # 空の値を除外
        ame_rooms = data.getlist('amenity')
        ame_rooms = [x for x in ame_rooms if x]  # 空の値を除外
        duvet_rooms = data.getlist('duvet')
        duvet_rooms = [x for x in duvet_rooms if x]
        
        rooms_rooms_per_person = data.getlist('rooms')
        person_rooms_per_person = data.getlist('persons')
        
        not_clean_required = data.getlist('not_clean_required')
        not_clean_required = [x for x in not_clean_required if x]  # 空の値を除外
        
        free_constraints = data.getlist('free_constraints')
  
        #Tが変数ならTrue、それ以外をFalseに変換
        house_is_least_comfort = [True if x == 'T' else False for x in house_is_least_comfort]
        house_is_bath = [True if x == 'T' else False for x in house_is_bath]
        
        #ハウスデータのうち、最も少ない配列要素数に合わせる
        min_length = min(len(house_no), len(house_name), len(house_max), len(house_least_floor), 
                         len(house_is_least_comfort), len(house_is_bath))
        #ハウスデータまとめ
        house_data = []
        house_secret_list = []
        alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        for i in range(min_length):
            no = house_no[i]
            name = alphabet[i]
            tmp = [alphabet[i], house_name[i]]
            house_secret_list.append(tmp)
            key = {
                'max': house_max[i],
                'least_floor': house_least_floor[i],
                'is_least_comfort': house_is_least_comfort[i],
                'is_bath': house_is_bath[i],
            }
            if no and name:
                house_data.append([no, name, key])
        
        room_per_person = []
        for i in range(len(rooms_rooms_per_person)):
            if rooms_rooms_per_person[i] and person_rooms_per_person[i]:
                room_per_person.append({
                    'room': rooms_rooms_per_person[i],
                    'person': person_rooms_per_person[i]
                })
        
        #toAPIデータ取りまとめ
        total_data = {
            'today': today,
            'eco_rooms': eco_rooms,
            'ame_rooms': ame_rooms,
            'duvet_rooms': duvet_rooms,
            'not_clean_required': not_clean_required,
            'house_data': house_data,
            'free_constraints': free_constraints,
            'room_per_person': room_per_person,
        }
        
        #OpenAI APIを呼び出す
        if os.path.exists(os.path.join('static/openai.json')):
            with open(os.path.join('static/openai.json')) as openai_file:
                openai_info = json.load(openai_file)
        else:
            print('openai.json could not be found.')
            quit()
        
        with open('static/prompt/openAI.txt', 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        openai.api_key = openai_info['api_key']
        try:
            response = openai.ChatCompletion.create(
                model=openai_info['model'],
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(total_data, ensure_ascii=False)
                    }
                ],
                temperature=0.7,
            )
            result = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return JsonResponse({'error': 'OpenAI API error'}, status=500)
        
        print(result)
        
        context = {}
        return render(self.request, self.res_template_name, context)
    