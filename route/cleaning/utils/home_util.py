import csv
from collections import defaultdict

def read_csv():
    with open('static/room_info.csv', 'r') as f:
        reader = csv.reader(f)
        room_info_raw_data = [row for row in reader]
    with open('static/times_by_type.csv', 'r') as f:
        reader = csv.reader(f)
        times_by_time_raw_data = [row for row in reader]
    with open('static/master_key.csv', 'r') as f:
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

