from django.shortcuts import redirect
from django.urls import reverse
from ..utils.sidewind_core import assign_rooms
from ..utils.home_util import read_csv
from ..utils.preview_util import multiple_night, multiple_night_cleans, get_cover, catch_post
import datetime
from collections import Counter, defaultdict, OrderedDict

def verify_quota_match(rooms, eco_rooms, eco_out_rooms, housekeepers, twin_rooms):
    """
    quota合計と通常清掃部屋数（eco・eco外を除く）の整合性を検証する。
    また、twin_quota合計とツイン部屋数の整合性も検証する。

    Parameters
    ----------
    rooms : dict or list
        全ての清掃対象部屋（通常・エコ・エコ外を含む）。
        dictの場合は len(rooms) を使用。
    eco_rooms : list[int]
        エコ清掃部屋番号リスト。
    eco_out_rooms : list[int]
        エコ外清掃部屋番号リスト。
    housekeepers : list[dict]
        各ハウスキーパー設定（例: {'id':1, 'room_quota':6, 'twin_quota':2, 'has_bath':True}）
    twin_rooms : list[int]
        ツイン部屋のリスト

    Raises
    ------
    RuntimeError
        quota合計と「通常清掃部屋数」が一致しない場合、または
        twin_quota合計と「ツイン部屋数」が一致しない場合。
    """
    # 全対象部屋から通常清掃部屋だけを抽出
    all_room_ids = list(rooms.keys()) if isinstance(rooms, dict) else list(rooms)
    eco_set = set(eco_rooms + eco_out_rooms)
    normal_rooms = [r for r in all_room_ids if r not in eco_set]

    # 通常部屋数
    total_rooms = len(normal_rooms)
    # quota合計（エコ部屋は含まない）
    total_quota = sum(h["room_quota"] for h in housekeepers)

    if total_quota != total_rooms:
        diff = total_quota - total_rooms
        msg = (
            f"Quota mismatch detected!\n"
            f" - Total normal rooms : {total_rooms}\n"
            f" - Total quota        : {total_quota}\n"
            f" - Difference         : {diff} ({'over' if diff>0 else 'under'})\n\n"
            f"quota（通常部屋数の割り当て数）が全通常部屋数と一致していません。\n"
            f"eco/eco外部屋はquota計算に含まれません。"
        )
        raise RuntimeError(msg)
    else:
        print(f"Quota check passed: {total_rooms} normal rooms = total quota {total_quota}")

    # T部屋数の検証（指定されている場合のみ）
    twin_set = set(twin_rooms)
    twin_in_normal = [r for r in normal_rooms if r in twin_set]
    total_twin_rooms = len(twin_in_normal)
    total_twin_quota = sum(h.get("twin_quota", 0) for h in housekeepers)


def sidewind_front(request):
    if request.method == 'POST': 
        #POSTデータ受け取り
        name = request.POST.get('editor_name')
        date = request.POST.get('date')
        single_time = int(request.POST.get('single_time'))
        twin_time = int(request.POST.get('twin_time'))
        bath_time = int(request.POST.get('bath_time'))
        
        #quota関連処理
        post_quota = []
        for i in range(1, 21):
            room_num = request.POST.get(f'room_num_{i}')
            house_person = request.POST.get(f'house_person_{i}')
            twin_room = request.POST.get(f'twin_room_{i}')
            public_bath = request.POST.get(f'public_bath_{i}')
            if public_bath == 'on':
                public_bath = True
            else:
                public_bath = False
                
            if any(x != None for x in (room_num, house_person)):
                if len(room_num) != 0 and len(house_person) != 0:
                    post_quota.append([room_num, house_person, twin_room if twin_room and len(twin_room) > 0 else '-1', public_bath])
        housekeepers = []
        id = 1
        for i in post_quota:
            for j in range(int(i[1])):
                housekeepers.append({'id':id, 'room_quota':int(i[0]), 'twin_quota':int(i[2]), 'has_bath':i[3]})
                id += 1
        
        #部屋処理
        eco_rooms = [int(x) for x in request.POST.getlist('eco_room') if x != '']
        eco_out_rooms = [int(x) for x in request.POST.getlist('amenity') if x != '']
        duvet_rooms = [int(x) for x in request.POST.getlist('duvet') if x != '']

        #連泊入力の受け取り
        try:
            multiple_rooms = multiple_night(request)
        except Exception as e:
            multiple_rooms = []

        #連泊清掃入力の受け取り
        try:
            multiple_night_cleans_list = multiple_night_cleans(request)
        except Exception as e:
            multiple_night_cleans_list = []

        #カバー情報の受け取り（ルームチェンジ、アウトイン、要清掃、その他備考）
        try:
            room_changes, outins, must_cleans, others, _ = get_cover(request)
        except Exception as e:
            room_changes = []
            outins = []
            must_cleans = []
            others = ''

        #その他の情報を取得
        try:
            _, _, _, _, _, bath_person, remarks, house_data, _, _, _, _, _, _, contacts, spots = catch_post(request)
        except Exception as e:
            bath_person = []
            remarks = []
            house_data = []
            contacts = []
            spots = []

        room_info_data, times_by_time_data, master_key_data = read_csv()
        twin_rooms = [int(x[0]) for x in room_info_data if x[1] == 'T']
        room_inputs = {}  # { room_number: value }
        for key, value in request.POST.items():
            if key.startswith("room_"):
                room_number = key.replace("room_", "")
                if len(room_number) < 5:    
                    room_inputs[room_number] = value.strip()
        full_clean_rooms = []
        for room, status in room_inputs.items():
            if status != '0' and room not in eco_out_rooms and room not in eco_rooms :
                full_clean_rooms.append(int(room))
        full_clean_rooms = sorted(full_clean_rooms,key=int)
        
        eco_time = int(times_by_time_data[3][1])
        all_rooms = [int(x[0]) for x in room_info_data]
        
        no_clean_rooms = [int(r) for r in all_rooms if r not in full_clean_rooms + eco_rooms + eco_out_rooms]
        rooms = {r: None for r in full_clean_rooms if r not in eco_rooms + eco_out_rooms}
        
        #清掃部屋数とquotaの整合性確認
        verify_quota_match(rooms, eco_rooms, eco_out_rooms, housekeepers, twin_rooms)
        
        #実行
        # bath_roomsは現時点では空リストとして扱う（将来的には大浴場の部屋番号を指定可能）
        bath_rooms = []
        print(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers, single_time, twin_time, eco_time, bath_time)
        allocation = assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, bath_rooms, housekeepers, single_time, twin_time, eco_time, bath_time)

        
        all_allocation = allocation

        # ============================================================
        #  出力
        # ============================================================
        print(f"\n全室数: {len(all_rooms)}室")
        print(f"清掃不要部屋: {len(no_clean_rooms)}室")
        print(f"通常清掃部屋: {len(rooms)}室")
        print(f"エコ部屋: {len(eco_rooms)}室 / エコ外: {len(eco_out_rooms)}室")

        #print("\n=== 自動割り当て結果（全室・上位表示） ===")
        for r in sorted(all_allocation.keys()):
            tag = ""
            if r in eco_rooms:
                tag = "（エコ）"
            elif r in eco_out_rooms:
                tag = "（エコ外）"
            elif r in twin_rooms:
                tag = "（ツイン）"
            #print(f"部屋 {r:4} → ハウス {all_allocation[r]} {tag}")

        # ---------- ハウス別集計 ----------
        print("\n=== ハウス別担当数 ===")
        eco_set = set(eco_rooms + eco_out_rooms)
        normal_set = set(rooms.keys())  # 通常部屋のみ

        normal_count = {}
        eco_count = {}
        total_count = {}

        for h in housekeepers:
            hid = h["id"]

            # ←ここを修正：「通常部屋集合」のみ対象にする
            normal = sum(1 for r in normal_set if all_allocation.get(r) == hid)

            # eco部屋は別集合でカウント
            eco = sum(1 for r in eco_set if all_allocation.get(r) == hid)

            total = normal + eco
            normal_count[hid] = normal
            eco_count[hid] = eco
            total_count[hid] = total

            print(f"ハウス{hid:2}: 通常={normal:2d} / エコ={eco:2d} / 合計={total:2d} ")

        print(f"\n合計: 通常={sum(normal_count.values())} / エコ={sum(eco_count.values())} / 全体={sum(total_count.values())}")

        # ---------- ツイン数分布 ----------
        print("\n=== ハウス別ツイン数 ===")
        for h in housekeepers:
            hid = h["id"]
            twins = sum(1 for r in twin_rooms if all_allocation.get(r) == hid)
            print(f"ハウス{hid:2}: ツイン={twins}")

        # ---------- ハウス別担当階 ----------
        print("\n=== ハウス別担当階 ===")
        floors_by_house = defaultdict(set)
        for r, hid in all_allocation.items():
            floors_by_house[hid].add(r // 100)

        for h in housekeepers:
            hid = h["id"]
            floors = sorted(floors_by_house[hid])
            floor_str = ", ".join(f"{f}F" for f in floors) if floors else "なし"
            print(f"ハウス{hid:2}: {floor_str}")
            
        # ---------- 接続用 ----------
        sorted_allocation = OrderedDict()

        # 全部屋番号を昇順にソートしてループ
        for r in sorted(all_rooms):
            if r in all_allocation:
                sorted_allocation[r] = all_allocation[r]
            else:
                sorted_allocation[r] = 0  # 未割当部屋はハウス0として扱う

        # 出力（人間可読 / JSON両対応）
        #print("\n=== 接続用データ配列（全室・未割当=0） ===")
        #print(sorted_allocation)
        
        print('eco_rooms:', eco_rooms)
        print('eco_out_rooms:', eco_out_rooms)
        print('allocation:', sorted_allocation)
        
        #セッション
        request.session['sidewind_flag'] = True
        request.session['allocation'] = sorted_allocation
        request.session['editor_name'] = name
        request.session['date'] = date
        request.session['single_time'] = single_time
        request.session['twin_time'] = twin_time
        request.session['bath_time'] = bath_time
        request.session['eco_rooms'] = eco_rooms
        request.session['ame'] = eco_out_rooms
        request.session['duvet'] = duvet_rooms
        request.session['multiple_rooms'] = multiple_rooms
        request.session['multiple_night_cleans'] = multiple_night_cleans_list
        request.session['room_changes'] = room_changes
        request.session['outins'] = outins
        request.session['must_cleans'] = must_cleans
        request.session['others'] = others
        request.session['remarks'] = remarks
        request.session['contacts'] = contacts
        request.session['spots'] = spots
        bath_staff = [h['id'] for h in housekeepers if h['has_bath']]
        request.session['bath_staff'] = bath_staff
        request.session['bath_person'] = bath_person
                
        return redirect(reverse('home'))
    return redirect(reverse('sidewind'))