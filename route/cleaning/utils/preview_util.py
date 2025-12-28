import datetime
import itertools
from ..utils.home_util import read_csv, dist_room
import requests
from googletrans import Translator
from typing import Optional
from deep_translator import GoogleTranslator
from google.cloud import translate_v2 as gct  
from typing import Optional

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
        eng = request.POST.get(f'eng_{i}')
        if eng == 'on':
            eng = True
        else:
            eng = False

        if any(x != '' for x in (name, key, dd)):
            house_data.append([no,name, key, dd,eng])
            
    spots = []
    # POST データの key を全部ループ
    for key in request.POST:
        if key.startswith("spot_number_"):
            index = key.split("_")[-1]  # 例: 'remark_room_3' → '3'
            room = request.POST.get(f"spot_number_{index}", "").strip()
            content = request.POST.get(f"spot_{index}", "").strip()
            # 両方に何か入力があるときだけ追加
            if room and content:
                spots.append({"room": room, "content": content})
        
    eco_rooms = request.POST.getlist("eco_room")
    ame_rooms = request.POST.getlist("amenity")           
    duvet_rooms = request.POST.getlist("duvet")  
    
    room_info_data, times_by_time_data, master_key_data = read_csv()
    single_rooms, twin_rooms = dist_room(room_info_data)
    return date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name, contacts, spots

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


    # -- 連泊新規清掃部屋 --
    multiple_night_clean_list = post.getlist("multiple_night_cleans")
    multiple_night_cleans = [] 
    for i in multiple_night_clean_list:
        if i != "":
            multiple_night_cleans.append(i)

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
    return room_changes, outins, must_cleans ,others, multiple_night_cleans
    
        

def is_bath(bath_person, person):
    if str(person) in bath_person:
        return True
    else:
        return False
    
def weekly_cleaning(date):
    #日付から曜日を取得
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    week = date.strftime('%A')
    return week
    
def calc_room(room_inputs, eco_rooms, duvet_rooms, ame_rooms, remarks, person, single_rooms, twin_rooms, multiple_rooms, outins, spots, lang):
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
        if lang == 'en':
            if len(remarks) == 0:
                if eco == True and ame == True:
                    if 'Eco-Outside' not in remark_comment:
                        remark_comment = 'Eco-Outside　' + remark_comment
                elif eco == True:
                    if 'Eco' not in remark_comment:
                        remark_comment = 'Eco　' + remark_comment

            else:
                for remark in remarks:
                    if room_num in remark['room']:
                        remark_tran = language(None, lang , remark['comment'])
                        if len(remark_comment) != 0:
                            remark_comment = remark_comment + '　' + remark_tran
                        else:
                            remark_comment = remark_tran
                        if eco == True and ame == True:
                            if 'Eco-Outside' not in remark_comment:
                                remark_comment = 'Eco-Outside　' + remark_comment
                        elif eco == True:
                            if 'Eco' not in remark_comment:
                                remark_comment = 'Eco　' + remark_comment
                    else:
                        if eco == True and ame == True:
                            if 'Eco-Outside' not in remark_comment:
                                remark_comment = 'Eco-Outside　' + remark_comment
                        elif eco == True:
                            if 'Eco' not in remark_comment:
                                remark_comment = 'Eco　' + remark_comment
        
        else:
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
                        if len(remark_comment) != 0:
                            remark_comment = remark_comment + '　' + remark['comment']
                        else:
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
            
        #スポットのリストを作成
        spot_comment = ''
        if len(spots) != 0:
            for spot in spots:
                if lang == 'en':
                    if room_num in spot['room']:
                        if len(remark_comment) != 0:
                            remark_comment = remark_comment + '　' + language(None,lang, spot['content'])
                            spot_comment = language(None,lang, spot['content'])
                        else:
                            remark_comment = language(None,lang, spot['content'])
                            spot_comment = language(None,lang, spot['content'])
                else:
                    if room_num in spot['room']:
                        if len(remark_comment) != 0:
                            remark_comment = remark_comment + '　' + spot['content']
                            spot_comment = spot['content']
                        else:
                            remark_comment = spot['content']
                            spot_comment = spot['content']
        
        
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
            
        #連泊部屋の処理
        if multiple_rooms and room_num in multiple_rooms:
            multiple = True
        else:
            if room_num in eco_rooms or room_num in ame_rooms or room_num in duvet_rooms:
                multiple = True
            else:
                multiple = False
                
        #アウトイン部屋の連泊処理
        if outins and room_num in outins:
            multiple = True
        
        room_info = {
            'room_num': room_num,
            'eco': eco,
            'duvet': duvet,
            'remark': remark_comment,
            'room_type': room_type,
            'multiple': multiple,
            'spot_content': spot_comment 
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

def changeDate(date_str,lang):
    # 日本語曜日に変換するためのリスト
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    weekday_map = ['月', '火', '水', '木', '金', '土', '日']
    weekday_map_eng = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if lang == 'ja':
        weekday_jp = weekday_map[date_obj.weekday()]
        date_jp = str(date_obj.month) + '月' + str(date_obj.day) + '日 ('+ weekday_jp + ')'
    else:
        weekday_en = weekday_map_eng[date_obj.weekday()]
        date_jp = date_obj.strftime(f"%b {date_obj.day}, %Y ({weekday_en})")
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
            spot_comment = room.get("spot_content", "").strip()
            if remark:  # 備考がある場合のみ
                result_remarks = remark
                if "エコ" in remark or "エコ外" in remark or "Eco" in remark or "Eco-Outside" in remark:
                    result_remarks = result_remarks.replace("エコ外", "").replace("エコ", "").replace("Eco-Outside", "").replace("Eco", "").strip()
                if spot_comment in result_remarks:
                    result_remarks = result_remarks.replace(spot_comment, "").strip()
                if result_remarks is not None and result_remarks.strip():
                    remarks_list.append((room_num, result_remarks, name))
    return remarks_list

def select_person_from_room_change(room_changes, key_name_list, rooms):
    result = []
    for i in room_changes:
        clean_original_flag = False
        clean_destination_flag = False
        for j in range(len(rooms)):
            for k in rooms[j]:
                if i['original'] in k['room_num']:
                    original_name = key_name_list[j][1]
                    clean_original_flag = True
                if i['destination'] in k['room_num']:
                    destination_name = key_name_list[j][1]
                    clean_destination_flag = True
            if clean_original_flag == False:
                original_name = '未販売部屋'
            if clean_destination_flag == False:
                destination_name = '未販売部屋'
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

def multiple_night(request):
    rooms = request.POST.getlist("multiple_night_room")
    rooms = [room.strip() for room in rooms if room.strip() != ""]
    return rooms

def multiple_night_cleans(request):
    cleans = request.POST.getlist("multiple_night_cleans")
    cleans = [clean.strip() for clean in cleans if clean.strip() != ""]
    return cleans

def google_translate_ja_to_en(text: Optional[str]) -> str:
    if not text:
        return ""
    try:
        # 重要: 4.0.0-rc1 を使用し、service_urls を指定
        from googletrans import Translator  # type: ignore
        translator = Translator(
            service_urls=[
                "translate.google.co.jp", 
                "translate.google.com",
            ]
        )
        result = translator.translate(text, src="ja", dest="en")
        if isinstance(result.text, str) and result.text.strip():
            return result.text
    except Exception:
        pass

    try:
        return GoogleTranslator(source="ja", target="en").translate(text)
    except Exception:
        pass

    try:
        client = gct.Client()
        res = client.translate(text, source_language="ja", target_language="en")
        tr = res.get("translatedText")
        if isinstance(tr, str):
            return tr
    except Exception:
        pass
    return text

def google_trancelate(text: Optional[str]) -> str:
    return google_translate_ja_to_en(text)

def translate(text):
    #インターネット接続を確認
    try:
        # タイムアウト3秒でGoogle翻訳サイトにアクセスしてみる
        response = requests.get("https://translate.google.com/", timeout=3)
        if response.status_code == 200:
            res = google_trancelate(text)
        else:
            res = text
    except requests.RequestException:
        # 接続エラーやタイムアウト時はこちらへ
        res = text
    return res

def language(str_id, lang_id, text):
    language_dict = {
        'ja': {
            'charge':'担当',
            'title':'さん',
            'consecutive_nights':'連泊',
            'eco':'エコ',
            'duvet':'デュベ',
            'remark':'備考',
            'cleaned':'清掃済',
            'inspection':'インスペ',
            'public_bath_cleaning':'大浴場清掃',
            'public_bath_cleaning_please':'大浴場清掃よろしくお願いいたします。',
            'master_key_number':'マスターキー番号',
            'target_completion_time_for_cleaning':'清掃終了目標時間',
            'cleaning_completion_time':'清掃終了時間',
            'spot_cleaning':'スポット清掃',
            'meating':'ミーティング',
            'author':'作成者',
            'early_shift':'早番',
            'inspection_charge':'インスペクション',
            'sign':'印',
            'notice':'連絡事項',
            'special_cleaning':'特別清掃(該当に◯)',
            'line_first':'　棚卸　　草取り',
            'airconditioner_filter_cleaning':'エアコンフィルター清掃',
            'units':'台',
            'line_second':'新人研修　　改装関連',
            'line_third':'　　ミーティング参加',
            'room_number':'部屋番号',
            'forget':'忘れ物',
            'hotel_name':'ルートイン水海道駅前',
            'declaration':'上記日程を終了致しました。',
            'signature':'(清掃担当者)署名　　　　　　　　　　',
            'Monday':'冷蔵庫上のほこり取り・机下面の清掃お願いします',
            'Tuesday':'内階段清掃お願いします',
            'Wednesday':'ズボンプレッサー清掃お願いします',
            'Thursday':'バスユニットのアメニティの皿清掃お願いします',
            'Friday':'加湿器フィルター清掃お願いします',
            'Saturday':'客室壁側面・天井付近クモの巣ほこり取りお願いします',
            'Sunday':'ドアのふち拭き上げお願いします'
        },
        'en': {
            'charge':'Charge',
            'title':'',
            'consecutive_nights':'Consecutive Nights',
            'eco':'Eco',
            'duvet':'Duvet',
            'remark':'Remark',
            'cleaned':'Cleaned',
            'inspection':'Inspection',
            'public_bath_cleaning':'Public Bath Cleaning',
            'public_bath_cleaning_please':'Please clean the public bath.',
            'master_key_number':'Master Key Number',
            'target_completion_time_for_cleaning':'Target Completion Time for Cleaning',
            'cleaning_completion_time':'Cleaning Completion Time',
            'spot_cleaning':'Spot Cleaning',
            'meating':'Meeting',
            'author':'Author',
            'early_shift':'Early Shift',
            'inspection_charge':'Inspection Charge',
            'sign':'Stamp',
            'notice':'Notice',
            'special_cleaning':'Special Cleaning (Circle if applicable)',
            'line_first':'Inventory　　Weeding',
            'airconditioner_filter_cleaning':'Air Conditioner Filter Cleaning',
            'units':'Units',
            'line_second':'New Employee Training　　Renovation Related',
            'line_third':'　　　Meeting Participation',
            'room_number':'Number',
            'forget':'Forgotten Items',
            'hotel_name':'RouteInn Mizkaido',
            'declaration':'The above schedule has been completed.',
            'signature':"(Cleaning Staff) Signature　　　　　　　　　　",
            'Monday':'Please clean the dust above the refrigerator and under the desk.',
            'Tuesday':'Please clean the indoor stairs.',
            'Wednesday':'Please clean the trouser press.',
            'Thursday':'Please clean the amenity dishes in the bath unit.',
            'Friday':'Please clean the humidifier filter.',
            'Saturday':'Please clean the cobwebs and dust on the side walls and ceilings of the guest rooms.',
            'Sunday':'Please wipe the edges of the doors.'
        }
    }
    if str_id != None and lang_id in language_dict:
        return language_dict[lang_id].get(str_id, str_id)
    else:
        res = translate(text)
        return res