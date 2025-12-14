from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.mail import send_mail
import json
import os

class reportView(TemplateView):
    template_name = "report.html"
    def get(self, request, *args, **kwargs):
        context = {}
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        #データ取得
        emargency_level = request.POST.get('emargency_level')
        genre = request.POST.get('genre')
        detail = request.POST.get('detail')
        
        #メールメッセージ作成
        if emargency_level == 'A':
            emargency_level = '緊急度A -直ちに開発者の対応が必要-'
        elif emargency_level == 'B':
            emargency_level = '緊急度B -数週間以内の対応が必要-'
        elif emargency_level == 'C':
            emargency_level = '緊急度C -数ヶ月以内の対応が必要-'
        elif emargency_level == 'D':
            emargency_level = '緊急度D -緊急ではない-'
        if genre == 'bug':
            genre = '不具合レポート'
        elif genre == 'data':
            genre = 'データ異常'
        elif genre == 'security':
            genre = 'セキュリティインシデント'
        elif genre == 'feature':
            genre = '機能追加要望'
        elif genre == "performance":
            genre = 'パフォーマンス改善要望'
        elif genre == 'usability':
            genre = 'ユーザビリティ改善要望'
        elif genre == 'other':
            genre = 'その他'
        message = "送信者：" + name + "\n" + "緊急度：" + emargency_level + "\n" + "ジャンル：" + genre + "\n" + "詳細：" + detail
        
        #送信先取得
        if os.path.exists(os.path.join('static/email.json')):
            with open(os.path.join('static/email.json')) as email_file:
                email_info = json.load(email_file)
        else:
            print('email.json could not be found.')
            quit()
        
        #メール送信
        send_mail(
            'route294(清掃指示書作成支援システム)からのレポート',  # 件名
            message,  # メッセージ
            email_info['address'],  # 送信元のメールアドレス
            [email_info['developer_address']],
            fail_silently=False,
        )
        context = {}
        return redirect('/?from_report=1')
