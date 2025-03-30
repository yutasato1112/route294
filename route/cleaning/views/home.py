from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
import datetime

from ..utils.home_util import read_csv, processing_list

# Create your views here.

class homeView(TemplateView):
    template_name = "home.html"
    
    def get(self, request, *args, **kwargs):
        #初回アクセス時
        #csv読み込み
        room_info_data, times_by_time_data = read_csv()
        
        #部屋を階別に二次元配列へ加工
        room_num_table = processing_list(room_info_data)
        
        #日付取得
        today = datetime.date.today()
        
        context = {
            'single_time':int(times_by_time_data[0][1]),
            'twin_time':int(times_by_time_data[1][1]),
            'bath_time':int(times_by_time_data[2][1]),
            'today':today,
            'rooms':room_num_table,
        }
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = {}
        return render(self.request, self.template_name, context)
