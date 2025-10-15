from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime
import json
from django.http import JsonResponse
from urllib.parse import urlparse
from ..utils.preview_util import catch_post, multiple_night
from ..utils.home_util import read_csv, processing_list, dist_room, room_person, room_char
#from openai import OpenAI
import os
import traceback
# Create your views here.

class sidewindView(TemplateView):
    template_name = "sidewind.html"
    def get(self, request, *args, **kwargs):
        method = 'GET'
        context={}
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        method = 'POST'
        #データ受け取り
        date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name, contacts, spots = catch_post(request)

        #連泊入力の受け取り
        try:
            multiple_rooms = multiple_night(request)
        except Exception as e:
            multiple_rooms = []
        
        #csv読み込み
        room_info_data, times_by_time_data, master_key_data = read_csv()
        #部屋を階別に二次元配列へ加工
        room_num_table = processing_list(room_info_data)
        #部屋をタイプ別に一次元配列に加工
        single_room_list, twin_room_list = dist_room(room_info_data)
        
        #部屋情報の表示用リスト作成
        combined_rooms = room_person(room_num_table, room_inputs)
        for floor in combined_rooms:
            for room in floor:
                    if room['status'] != '' and room['status'] != 0:
                        room['status'] = ''
        
        #エコ・アメ・デュべ部屋の処理
        room_char_list = room_char(eco_rooms, ame_rooms, duvet_rooms)

        if len(room_char_list) < 10:
            room_char_list_len = 10-len(room_char_list)
        else:
            room_char_list_len = 1

        context = {
            'method':method,
            'editor_name':editor_name,
            'single_time':single_time,
            'twin_time':twin_time,
            'bath_time':bath_time,
            'today':datetime.datetime.strptime(date, '%Y-%m-%d').date(),
            'combined_rooms':combined_rooms,
            'room_char_list_len':room_char_list_len,
            'eco_rooms':eco_rooms,
            'ame_rooms':ame_rooms,
            'duvet_rooms':duvet_rooms,
            'room_char_list':room_char_list,
            'quota_len':10
        }
        return render(self.request, self.template_name, context)
    