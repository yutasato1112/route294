import datetime
import itertools
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
            if len(room_number) < 5:    
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
    # POST データの key を全部ループ
    contacts = []
    for key in request.POST:
        if key.startswith("contact_number_"):
            index = key.split("_")[-1]  # 例: 'remark_room_3' → '3'
            number = request.POST.get(f"contact_number_{index}", "").strip()
            contact = request.POST.get(f"contact_{index}", "").strip()
            # 両方に何か入力があるときだけ追加
            if number and contact:
                contacts.append({"person_number": number, "contact": contact})

    house_data = []
    for i in range(1, 100):  # 最大100人分を仮定
        no = request.POST.get(f'no_{i}', '').strip()
        name = request.POST.get(f'name_{i}', '').strip()
        key = request.POST.get(f'key_{i}', '').strip()
        dd = request.POST.get(f'dd_{i}', '').strip()

        if any(x != '' for x in (name, key, dd)):
            house_data.append([no,name, key, dd])
        
    eco_rooms = request.POST.getlist("eco_room")
    ame_rooms = request.POST.getlist("amenity")           
    duvet_rooms = request.POST.getlist("duvet")  
    
    room_info_data, times_by_time_data, master_key_data = read_csv()
    single_rooms, twin_rooms = dist_room(room_info_data)
    return date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name, contacts

def get_cover(request):
    post = request.POST
    # --- ルームチェンジ ---
    room_changes = []
    i = 1
    original_list = post.getlist("room_change_original")
    destination = post.getlist("room_change_destination")
    for i in range(len(original_list)):
        if original_list[i] != "" and destination[i] != "":
            room_changes.append({"original": original_list[i], "destination": destination[i]})


    # --- アウトイン ---
    outin_list = post.getlist("outin")
    outins = []
    for i in outin_list:
        if i != "":
            outins.append(i)

    # --- 要清掃 ---
    must_cleans = []
    must_clean_room_tmp = post.getlist("must_clean_room")
    must_clean_room_to_tmo = post.getlist("must_clean_room_to")
    must_clean_reason_tmp = post.getlist("must_clean_reason")
    must_clean_room = []
    must_clean_room_to = []
    must_clean_reason = []
    for i in must_clean_room_tmp:
        if i != '':
            must_clean_room.append(i)
    for i in must_clean_room_to_tmo:
        if i != '':
            must_clean_room_to.append(i)
    for i in must_clean_reason_tmp:
        if i != '':
            must_clean_reason.append(i)
    
    for i in range(len(must_clean_room)):
        if must_clean_room[i] != '':
            must_cleans.append({"room":must_clean_room[i],"room_to":must_clean_room_to[i] , "reason":must_clean_reason[i]})
    # --- その他備考 ---
    others = post.get("others", "").strip()
    return room_changes, outins, must_cleans ,others
    
        

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
    
def calc_room(room_inputs, eco_rooms, duvet_rooms, ame_rooms, remarks, person, single_rooms, twin_rooms):
    #ルームナンバーのリストを作成
    room_nums = []
    for key, value in room_inputs.items():
        if str(person) in value:
            value_str = str(value)
            person_str = str(person)
            if len(person_str) == len(value_str):
                room_nums.append(key)
    #ルームナンバーのリストをソート
    manage_rooms = []
    room_nums.sort(key=lambda x: int(x))
    floor = []
    for room_num in room_nums:
        eco = False
        duvet = False
        ame = False
        remark_comment = ''
        #eco_roomsのリストを作成
        if room_num in eco_rooms:
            eco = True
        #ame_roomsのリスト作成
        if room_num in ame_rooms:
            ame = True
        #duvet_roomsのリストを作成
        if room_num in duvet_rooms:
            duvet = True
        #remarksのリストを作成
        if len(remarks) == 0:
            if eco == True and ame == True:
                if 'エコ外' not in remark_comment:
                    remark_comment = 'エコ外　' + remark_comment
            elif eco == True:
                if 'エコ' not in remark_comment:
                    remark_comment = 'エコ　' + remark_comment

        else:
            for remark in remarks:
                if room_num in remark['room']:
                    remark_comment = remark['comment']
                    if eco == True and ame == True:
                        if 'エコ外' not in remark_comment:
                            remark_comment = 'エコ外　' + remark_comment
                    elif eco == True:
                        if 'エコ' not in remark_comment:
                            remark_comment = 'エコ　' + remark_comment
                else:
                    if eco == True and ame == True:
                        if 'エコ外' not in remark_comment:
                            remark_comment = 'エコ外　' + remark_comment
                    elif eco == True:
                        if 'エコ' not in remark_comment:
                            remark_comment = 'エコ　' + remark_comment

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

def search_bath_person(bath_person, key_name_list):
    name_list = []
    for i in bath_person:
        for j in key_name_list:
            if str(i) == str(j[0]):
                name_list.append(j[1])
                break
    return name_list

def search_remarks_name_list(key_name_list, rooms):
    remarks_list = []
    for i, person_rooms in enumerate(rooms):
        name = key_name_list[i][1]
        for room in person_rooms:
            remark = room.get("remark", "").strip()
            room_num = room.get("room_num", "")
            if remark:  # 備考がある場合のみ
                if remark !="エコ" and remark != "エコ外":
                    remarks_list.append((room_num, remark.replace("エコ外", "").replace("エコ", "").strip(), name))
    return remarks_list

def select_person_from_room_change(room_changes, key_name_list, rooms):
    result = []
    for i in room_changes:
        for j in range(len(rooms)):
            for k in rooms[j]:
                if i['original'] in k['room_num']:
                    original_name = key_name_list[j][1]
                if i['destination'] in k['room_num']:
                    destination_name = key_name_list[j][1]
        tmp = {'original':i['original'], 'original_name':original_name, 'destination':i['destination'], 'destination_name':destination_name}
        result.append(tmp)
    return result

def add_rc(total_data, room_changes_person):
    for person in total_data:
        for room_info in person['rooms']:
            for rc in room_changes_person:
                if room_info['room_num'] == rc['original']:
                    if len(room_info['remark']) != 0:
                        room_info['remark'] = room_info['remark'] + '　R/C #'+ rc['destination'] + 'へ('+ rc['destination_name'] +'さん)'
                    else:
                        room_info['remark'] = 'R/C #'+ rc['destination'] + 'へ('+ rc['destination_name'] +'さん)'
                elif room_info['room_num'] == rc['destination']:
                    if len(room_info['remark']) != 0:
                        room_info['remark'] = room_info['remark'] + '　R/C #'+ rc['original'] + 'から('+ rc['original_name'] +'さん)'
                    else:
                        room_info['remark'] = 'R/C #'+ rc['original'] + 'から('+ rc['original_name'] +'さん)'
    return total_data

def split_contact_textarea(contact_text):
    def split_by_length(s, max_len=20):
        return [s[i:i+max_len] for i in range(0, len(s), max_len)]

    # 改行コードの統一
    lines = contact_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    # 各行を20文字ごとに分割し、flattenする
    processed_lines = []
    for line in lines:
        processed_lines.extend(split_by_length(line.strip(), 20))

    # contact_1～contact_4までを取り、残りはcontact_4にまとめて格納
    contact_1 = processed_lines[0] if len(processed_lines) > 0 else ''
    contact_2 = processed_lines[1] if len(processed_lines) > 1 else ''
    contact_3 = processed_lines[2] if len(processed_lines) > 2 else ''
    contact_4 = '\n'.join(processed_lines[3:]) if len(processed_lines) > 3 else ''
    return contact_1, contact_2, contact_3, contact_4
    
def calc_room_type_count(rooms):
    single = 0
    single_eco = 0
    twin = 0
    twin_eco = 0
    
    for room in rooms:
        if room['room_type'] == 'S':
            if room['eco'] == True:
                single_eco += 1
            else:
                single += 1
        elif room['room_type'] == 'T':
            if room['eco'] == True:
                twin_eco += 1
            else:
                twin += 1
    room_type_count_str = f"S:{single}, SE:{single_eco}, T:{twin}, TE:{twin_eco}"
    return room_type_count_str

def calc_DD_list(house_data):
    assignments = []
    for i in house_data:
        dd = i[3]
        if dd != '':
            # DDのリストを作成
            dd_list = []
            for j in dd.split(','):
                if j != '':
                    dd_list.append(j)
            assignments.append(dd_list)
        else:
            assignments.append(None)
    result = [
                None if x is None else " ".join(f"{i}F D.D." for i in x)
                for x in assignments
            ]
    return result

def calc_cover_remarks(remarks_name_list, remarks):
    remarks_name_list_rooms = {room for room, _, _ in remarks_name_list}
    diff = [item for item in remarks if item['room'] not in remarks_name_list_rooms]
    for i in diff:
        remarks_name_list.append((i['room'], i['comment'], '　　　　'))
    return remarks_name_list

def special_clean(request):
    is_drain_water = request.POST.get('drain_water', 'off') == 'on'
    is_highskite = request.POST.get('highskit', 'off') == 'on'
    is_chlorine = request.POST.get('chlorine', 'off') == 'on'
    is_chemical_clean = request.POST.get('chemical_clean', 'off') == 'on'
    is_public = request.POST.get('public', 'off') == 'on'
    return is_drain_water, is_highskite, is_chlorine, is_chemical_clean, is_public