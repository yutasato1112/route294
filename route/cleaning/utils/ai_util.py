from ..utils.home_util import read_csv, processing_list, dist_room, room_person, room_char
import datetime

def get_data(request):
    date = request.GET.get('date')
    single_time = request.GET.get('single_time')
    twin_time = request.GET.get('twin_time')
    bath_time = request.GET.get('bath_time')
    editor_name = request.GET.get('editor_name')
    room_inputs = {}  # { room_number: value }
    for key, value in request.GET.items():
        if key.startswith("room_"):
            room_number = key.replace("room_", "")
            if len(room_number) < 5:    
                room_inputs[room_number] = value.strip()
    
    bath_person = request.GET.getlist("bath") 
    
    remarks = []
    # GET データの key を全部ループ
    for key in request.GET:
        if key.startswith("remark_room_"):
            index = key.split("_")[-1]  # 例: 'remark_room_3' → '3'
            room = request.GET.get(f"remark_room_{index}", "").strip()
            comment = request.GET.get(f"remark_{index}", "").strip()

            # 両方に何か入力があるときだけ追加
            if room and comment:
                remarks.append({"room": room, "comment": comment})
    
    # GET データの key を全部ループ
    contacts = []
    for key in request.GET:
        if key.startswith("contact_number_"):
            index = key.split("_")[-1]  # 例: 'remark_room_3' → '3'
            number = request.GET.get(f"contact_number_{index}", "").strip()
            contact = request.GET.get(f"contact_{index}", "").strip()
            # 両方に何か入力があるときだけ追加
            if number and contact:
                contacts.append({"person_number": number, "contact": contact})

    house_data = []
    for i in range(1, 100):  # 最大100人分を仮定
        no = request.GET.get(f'no_{i}', '').strip()
        name = request.GET.get(f'name_{i}', '').strip()
        key = request.GET.get(f'key_{i}', '').strip()
        dd = request.GET.get(f'dd_{i}', '').strip()

        if any(x != '' for x in (name, key, dd)):
            house_data.append([no,name, key, dd])
        
    eco_rooms = request.GET.getlist("eco_room")
    ame_rooms = request.GET.getlist("amenity")           
    duvet_rooms = request.GET.getlist("duvet")  
    
    room_info_data, times_by_time_data, master_key_data = read_csv()
    single_rooms, twin_rooms = dist_room(room_info_data)
    data = {
        'editor_name': editor_name,
        'date': date,
        'single_time': single_time,
        'twin_time': twin_time,
        'bath_time': bath_time,
        'room_inputs': room_inputs,
        'bath_person': bath_person,
        'house_data': house_data,
        'eco_rooms': eco_rooms,
        'ame_rooms': ame_rooms,
        'duvet_rooms': duvet_rooms,
        'single_rooms': single_rooms,
        'twin_rooms': twin_rooms,
    }
    return data

def processing_input_rooms(room_inputs):
    for key, value in room_inputs.items():
        if value != '0':
            room_inputs[key] = ''
    return room_inputs

def get_post_data(request):
    data = request.POST
    editor_name = data.get('editor_name')
    date_str = data.get('date')
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    single_time = int(data.get('single_time'))
    twin_time = int(data.get('twin_time'))
    bath_time = int(data.get('bath_time'))
    room_inputs = data.getlist('room_inputs')
    bath_persons = data.getlist('bath_person')
    house_person = data.getlist('house_person')
    eco_rooms = data.getlist('eco_rooms')
    ame_rooms = data.getlist('ame_rooms')
    duvet_rooms = data.getlist('duvet_rooms')
    constraints = data.getlist('constraints')

    return {
        'editor_name': editor_name,
        'date': date,
        'single_time': single_time,
        'twin_time': twin_time,
        'bath_time': bath_time,
        'room_inputs': room_inputs,
        'bath_persons': bath_persons,
        'house_person': house_person,
        'eco_rooms': eco_rooms,
        'ame_rooms': ame_rooms,
        'duvet_rooms': duvet_rooms,
        'constraints': constraints,
    }