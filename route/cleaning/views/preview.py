from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from ..utils.preview_util import catch_post, is_bath, weekly_cleaning,calc_room, calc_end_time, changeDate, search_bath_person, search_remarks_name_list, get_cover, select_person_from_room_change

# Create your views here.

class previewView(TemplateView):
    template_name = "preview.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        #データ受け取り
        date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name = catch_post(request)

        #表紙情報受け取り
        room_changes, outins, must_cleans, others = get_cover(request)
        
        #パーソン人数
        person_count = len(house_data)
        
        #部屋数のカウント
        total_cleaning_room = sum(1 for v in room_inputs.values() if v != '0')
        
        #大浴場追加要員
        original_add_bath = request.POST.getlist('bath_only')
        add_bath = []
        for i in original_add_bath:
            if i != '':
                add_bath.append(i)
        
        total_data = []
        #パーソンごとにデータを整理
        key_name_list = []
        rooms = []
        for i in range(person_count):
            name = house_data[i][1]
            key_name_list.append([house_data[i][0],name])
            key = house_data[i][2]
            bath = is_bath(bath_person, i+1)
            weekly = weekly_cleaning(date)
            room, floor = calc_room(room_inputs, eco_rooms, duvet_rooms, ame_rooms, remarks, i+1, single_rooms, twin_rooms)
            rooms.append(room)
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
                'room_changes':room_changes, 
                'outins':outins,
                'must_cleans':must_cleans,
                'othrts':others,
                'room_changes_len':len(room_changes),
                'outins_len':len(outins),
                'must_cleans_len':len(must_cleans),
            }
            total_data.append(persons_cleaning_data)
        #大浴場清掃担当者の名前リスト化
        bath_person_name = search_bath_person(bath_person, key_name_list)
        for i in add_bath:
            bath_person_name.append(i)
        
        #備考と名前のリスト化
        remarks_name_list = search_remarks_name_list(key_name_list, rooms)
        
        #ルームチェンジ情報とパーソンの突き合わせ
        room_changes_person = select_person_from_room_change(room_changes, key_name_list, rooms)
        
        #outin表示用加工
        outins_list = []
        for i in range(0, len(outins), 2):
            first = '　　　'+outins[i]
            second = '　　　'+outins[i+1] if i + 1 < len(outins) else '　　　　　'
            outins_list.append((first, second))
        
        context = {
            'data':total_data,
            'editor_name': editor_name,
            'date':date_jp,
            'house_person_count' : person_count,
            'total_cleaning_room':total_cleaning_room,
            'bath_person': bath_person_name,
            'remarks' : remarks_name_list,
            'room_changes_persons':room_changes_person,
            'outins':outins_list,
            'must_cleans':must_cleans,
            'others':others,
        }
        return render(self.request, self.template_name, context)
