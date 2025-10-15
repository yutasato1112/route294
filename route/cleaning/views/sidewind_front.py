from django.shortcuts import redirect
from django.urls import reverse
from ..utils.sidewind_core import assign_rooms
from ..utils.home_util import read_csv
import datetime
from collections import Counter, defaultdict, OrderedDict

def sidewind_front(request):
    if request.method == 'POST': 
        #POSTデータ受け取り
        name = request.POST.get('editor_name')
        date = datetime.datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date(),
        single_time = int(request.POST.get('single_time'))
        twin_time = int(request.POST.get('twin_time'))
        bath_time = int(request.POST.get('bath_time'))
        
        #quota関連処理
        post_quota = []
        for i in range(1, 21):
            room_num = request.POST.get(f'room_num_{i}')
            house_person = request.POST.get(f'house_person_{i}')
            public_bath = request.POST.get(f'public_bath_{i}')
            if public_bath == 'on':
                public_bath = True
            else:
                public_bath = False
                
            if any(x != None for x in (room_num, house_person)):
                if len(room_num) != 0 and len(house_person) != 0:
                    post_quota.append([room_num, house_person, public_bath])
        housekeepers = []
        id = 1
        for i in post_quota:
            for j in range(int(i[1])):
                housekeepers.append({'id':id, 'room_quota':int(i[0]), 'has_bath':i[2]})
                id += 1
        
        #部屋処理
        eco_rooms = [int(x) for x in request.POST.getlist('eco_room') if x != '']
        eco_out_rooms = [int(x) for x in request.POST.getlist('amenity') if x != '']
        duvet_rooms = [int(x) for x in request.POST.getlist('duvet') if x != '']
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
        rooms = {r: None for r in full_clean_rooms}
        
        #実行
        allocation = assign_rooms(rooms, eco_rooms, eco_out_rooms, twin_rooms, [], housekeepers,single_time, twin_time, eco_time, bath_time,)
        
        # 通常割り当て結果をもとに、eco/eco外もハウス数に応じて自動分配
        all_allocation = allocation.copy()

        # ルール: エコ部屋・エコ外も「近い階層の担当ハウス」に近似割り当て
        # ここでは単純に、同フロアで一番多いハウスを使う簡易ロジック
        # floor→house分布を構築
        floor_to_houses = defaultdict(list)
        for r, hid in allocation.items():
            floor_to_houses[r // 100].append(hid)

        def infer_house_for_floor(floor):
            counts = Counter(floor_to_houses[floor])
            return counts.most_common(1)[0][0] if counts else 1  # fallback

        # eco, eco外を近似割り当て
        for r in eco_rooms + eco_out_rooms:
            floor = r // 100
            inferred_h = infer_house_for_floor(floor)
            all_allocation[r] = inferred_h

        # ============================================================
        #  出力
        # ============================================================
        print(f"\n全室数: {len(all_rooms)}室")
        print(f"清掃不要部屋: {len(no_clean_rooms)}室")
        print(f"通常清掃部屋: {len(rooms)}室")
        print(f"エコ部屋: {len(eco_rooms)}室 / エコ外: {len(eco_out_rooms)}室")

        print("\n=== 自動割り当て結果（全室・上位表示） ===")
        for r in sorted(all_allocation.keys()):
            tag = ""
            if r in eco_rooms:
                tag = "（エコ）"
            elif r in eco_out_rooms:
                tag = "（エコ外）"
            elif r in twin_rooms:
                tag = "（ツイン）"
            print(f"部屋 {r:4} → ハウス {all_allocation[r]} {tag}")

        # ---------- ハウス別集計 ----------
        print("\n=== ハウス別担当数 ===")
        eco_set = set(eco_rooms + eco_out_rooms)
        normal_count = {}
        eco_count = {}
        total_count = {}

        for h in housekeepers:
            hid = h["id"]
            normal = sum(1 for r, hid2 in allocation.items() if hid2 == hid)
            eco = sum(1 for r in eco_set if all_allocation.get(r) == hid)
            total = normal + eco
            normal_count[hid] = normal
            eco_count[hid] = eco
            total_count[hid] = total
            print(f"ハウス{hid:2}: 通常={normal} / エコ={eco} / 合計={total} / quota={h['room_quota']}")

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
        print("\n=== 接続用データ ===")
        sorted_allocation = OrderedDict()

        # 全部屋番号を昇順にソートしてループ
        for r in sorted(all_rooms.keys()):
            if r in all_allocation:
                sorted_allocation[r] = all_allocation[r]
            else:
                sorted_allocation[r] = 0  # 未割当部屋はハウス0として扱う

        # 出力（人間可読 / JSON両対応）
        print("\n=== 接続用データ配列（全室・未割当=0） ===")
        print(sorted_allocation)
                
        
        return redirect(reverse('home'))
    return redirect(reverse('sidewind'))