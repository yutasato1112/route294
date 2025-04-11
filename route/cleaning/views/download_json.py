from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json
from ..utils.preview_util import catch_post
import datetime
import os


def download_json(request):
    if request.method == 'POST':
        date, single_time, twin_time, bath_time, room_inputs, bath_person, remarks, house_data, eco_rooms, ame_rooms, duvet_rooms, single_rooms, twin_rooms, editor_name = catch_post(request)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"worklog_{timestamp}.json"
        data = {
            'editor_name':editor_name,
            'date' : date,
            'single_time':single_time,
            'twin_time':twin_time,
            'bath_time':bath_time,
            'room_inputs':room_inputs,
            'bath_person':bath_person,
            'remarks':remarks,
            'house_data':house_data,
            'eco_rooms':eco_rooms,
            'ame_rooms':ame_rooms,
            'duvet_rooms':duvet_rooms,
        }
        

        # JSONに変換
        json_data = json.dumps(data, ensure_ascii=False, indent=2)

        # HTTPレスポンスにJSONファイルとして送信
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
       
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        with open(media_path, 'w', encoding='utf-8') as f:
            f.write(json_data)

        return response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
