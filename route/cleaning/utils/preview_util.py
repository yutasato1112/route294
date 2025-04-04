import datetime
from ..utils.home_util import read_csv, dist_room

def catch_post(request):
    date = request.POST.get('date')
    single_time = request.POST.get('single_time')
    twin_time = request.POST.get('twin_time')
    bath_time = request.POST.get('bath_time')
    editor_name = request.POST.get('editor_name')
    room_inputs = {}  # { room_number: value }
    for key, value in request.POST.items():
        if key.startswith("room_"):
            room_number = key.replace("room_", "")
            room_inputs[room_number] = value.strip()
    
    bath_person = request.POST.getlist("bath") 
    
    remarks = []
    # POST データの key を全部ループ
    for key in request.POST:
        if key.startswith("remark_room_"):
            index = key.split("_")[-1]  # 例: 'remark_room_3' → '3'
            room = request.POST.get(f"remark_room_{index}", "").strip()
            comment = request.POST.get(f"remark_{index}", "").strip()

            # 両方に何か入力があるときだけ追加
            if room and comment:
                remarks.append({"room": room, "comment": comment})
    
    house_data = []
    for i in range(1, 100):  # 最大100人分を仮定
        no = request.POST.get(f'no_{i}', '').strip()
        name = request.POST.get(f'name_{i}', '').strip()
        key = request.POST.get(f'key_{i}', '').strip()

        if no and name:
            house_data.append([no, name, key])
        
    eco_rooms = request.POST.getlist("eco_room")
    ame_rooms = request.POST.getlist("amenity")           
    duvet_rooms = request.POST.getlist("duvet")  
    
    room_info_data, times_by_time_data, master_key_data = read_csv()
    single_rooms, twin_rooms = dist_room(room_info_data)
    return date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name

def is_bath(bath_person, person):
    if str(person) in bath_person:
        return True
    else:
        return False
    
def weekly_cleaning(date):
    #日付から曜日を取得
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    week = date.strftime('%A')
    if week == 'Monday':
        return '冷蔵庫上のほこり取り・机下面の清掃お願いします'
    elif week == 'Tuesday':
        return '内階段清掃お願いします'
    elif week == 'Wednesday':
        return 'ズボンプレッサー清掃お願いします'
    elif week == 'Thursday':
        return 'バスユニットのアメニティの皿清掃お願いします'
    elif week == 'Friday':
        return '加湿器フィルター清掃お願いします'
    elif week == 'Saturday':
        return '客室壁側面・天井付近クモの巣ほこり取りお願いします'
    elif week == 'Sunday': 
        return 'ドアのふち拭き上げお願いします'
    else:
        return 'Invalid date'
    
def calc_room(room_inputs, eco_rooms, duvet_rooms, remarks, person, single_rooms, twin_rooms):
    #ルームナンバーのリストを作成
    room_nums = []
    for key, value in room_inputs.items():
        if str(person) in value:
            room_nums.append(key)
    #ルームナンバーのリストをソート
    manage_rooms = []
    room_nums.sort(key=lambda x: int(x))
    floor = []
    for room_num in room_nums:
        eco = False
        duvet = False
        remark_comment = ''
        #eco_roomsのリストを作成
        if room_num in eco_rooms:
            eco = True
        #duvet_roomsのリストを作成
        if room_num in duvet_rooms:
            duvet = True
        #remarksのリストを作成
        for remark in remarks:
            if room_num in remark['room']:
                remark_comment = remark['comment']
        #部屋タイプ
        room_type = 'E'
        if room_num in single_rooms:
            room_type = 'S'
        elif room_num in twin_rooms:
            room_type = 'T'
        
        #フロア
        if len(room_num) <= 3:
            floor.append(int(room_num[0]))
        else:
            floor.append(int(room_num[:2]))
        
        room_info = {
            'room_num': room_num,
            'eco': eco,
            'duvet': duvet,
            'remark': remark_comment,
            'room_type': room_type,
        }
        manage_rooms.append(room_info)
    floor_sorted = sorted(set(int(r) for r in floor))
    floor_list = list(map(str, floor_sorted))
    #ルームナンバーのリストを返す
    return manage_rooms, floor_list

def calc_end_time(single_time, twin_time, bath_time, bath, room, single_rooms, twin_rooms):
    #時間の計算
    single_time = int(single_time)
    twin_time = int(twin_time)
    bath_time = int(bath_time)
    total_time = 0
    for i in range(len(room)):
        if room[i]['eco'] == True:
            total_time += 5
        elif room[i]['room_num'] in single_rooms:
            total_time += single_time
        elif room[i]['room_num'] in twin_rooms:
            total_time += twin_time
    if bath == True:
        total_time += bath_time
    #時間の計算
    base_time = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=9, minute=30))
    end_time = base_time + datetime.timedelta(minutes=total_time)
    only_time = end_time.time()
    formatted = only_time.strftime("%H:%M")
    
    return formatted

def changeDate(date_str):
    # 日本語曜日に変換するためのリスト
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    weekday_map = ['月', '火', '水', '木', '金', '土', '日']
    weekday_jp = weekday_map[date_obj.weekday()]
    date_jp = str(date_obj.month) + '月' + str(date_obj.day) + '日 ('+ weekday_jp + ')'
    return date_jp