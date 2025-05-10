import csv
from collections import defaultdict

def read_csv():
    with open('static/csv/room_info.csv', 'r',encoding="utf-8") as f:
        reader = csv.reader(f)
        room_info_raw_data = [row for row in reader]
    with open('static/csv/times_by_type.csv', 'r',encoding="utf-8") as f:
        reader = csv.reader(f)
        times_by_time_raw_data = [row for row in reader]
    with open('static/csv/master_key.csv', 'r',encoding="utf-8") as f:
        reader = csv.reader(f)
        master_key_raw_data = [row for row in reader]
    room_info_data = room_info_raw_data[1:]
    times_by_time_data = times_by_time_raw_data[1:]
    master_key_data = master_key_raw_data[1:]
    return room_info_data, times_by_time_data, master_key_data


def processing_list(room_info_data):
    floors = defaultdict(list)
    for room, _ in room_info_data:
        floor = int(room) // 100  # 例: '201' → 2階
        floors[floor].append(room)
    room_num_table = [floors[f] for f in sorted(floors, reverse=True)]
    return room_num_table

def dist_room(room_info_data):
    single_room_list = []
    twin_room_list = []
    for room, room_type in room_info_data:
        if room_type == 'S':
            single_room_list.append(room)
        elif room_type == 'T':
            twin_room_list.append(room)
    return single_room_list, twin_room_list


def room_person(room_num_table, room_inputs):
    room_person = []
    for floor in room_num_table:
        tmp_room_person = []
        for room in floor:
            try:
                tmp_room_person.append(int(room_inputs[room]))
            except:
                tmp_room_person.append(None)
        room_person.append(tmp_room_person)
    combined_rooms = []
    for i in range(len(room_num_table)):
        floor_data = []
        for j in range(len(room_num_table[i])):
            if room_person[i][j] == None:
                status = ''
            else:
                status = room_person[i][j]
            floor_data.append({
                'room': room_num_table[i][j],
                'status': status,
            })
        combined_rooms.append(floor_data)
    return combined_rooms

def room_char(eco_rooms, ame_rooms, duvet_rooms):
    room_char = []
    eco_row = len(eco_rooms)//3
    if len(eco_rooms)%3 != 0:
        eco_row += 1
    ame_row = len(ame_rooms)//3
    if len(ame_rooms)%3 != 0:
        ame_row += 1
    duvet_row = len(duvet_rooms)//3
    if len(duvet_rooms)%3 != 0:
        duvet_row += 1
    total_row = max(eco_row, ame_row, duvet_row)
    
    for line_num in range(total_row):
        tmp_room_char = []
        #eco_room のスライスを line_num に応じて取る
        eco_line = eco_rooms[line_num * 3 : line_num * 3 + 3]
        tmp_room_char.append({'eco': eco_line})

        #ame_rooms[line_num] が IndexError の可能性があるのでチェック
        ame = ame_rooms[line_num] if line_num < len(ame_rooms) else ''
        tmp_room_char.append({'ame': ame})

        duvet_line = duvet_rooms[line_num * 2 : line_num * 2 + 2]
        tmp_room_char.append({'duvet': duvet_line})

        room_char.append(tmp_room_char)
    return room_char