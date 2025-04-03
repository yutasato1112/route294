def catch_post(request):
    date = request.POST.get('date')
    single_time = request.POST.get('single_time')
    twin_time = request.POST.get('twin_time')
    bath_time = request.POST.get('bath_time')
    
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
    return date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms 
