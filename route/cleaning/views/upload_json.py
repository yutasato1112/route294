from django.shortcuts import render
from django.http import JsonResponse
import json

def upload_json_view(request):
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        try:
            data = json.load(json_file)
            # ここでアップロードされたデータを使って何か処理をする
            print("アップロードされたデータ:", data)

            return JsonResponse({'message': 'JSONを正常に読み込みました'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSONの読み込みに失敗しました'}, status=400)

    return JsonResponse({'error': 'POSTリクエストとJSONファイルが必要です'}, status=400)
