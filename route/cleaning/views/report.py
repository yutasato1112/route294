from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.conf import settings
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path


LOG_DIR = Path(settings.BASE_DIR) / "logs"


def _collect_recent_logs(hours=24):
    """過去指定時間以内のログエントリを収集する"""
    cutoff = datetime.now() - timedelta(hours=hours)
    entries = []
    if not LOG_DIR.exists():
        return entries
    for path in sorted(LOG_DIR.glob("log_*.log"), reverse=True):
        # ファイル名から日付を取得し、明らかに古いファイルはスキップ
        m_file = re.search(r"log_(\d{8})\.log", path.name)
        if m_file:
            file_date = datetime.strptime(m_file.group(1), "%Y%m%d")
            if file_date.date() < (cutoff - timedelta(days=1)).date():
                continue
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} \[(\w+)\] (.*)$", line)
                if m:
                    ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                    if ts >= cutoff:
                        entries.append(f"[{m.group(1)}] [{m.group(2)}] {m.group(3)}")
                else:
                    # タイムスタンプなし行は直前のエントリに続くものとして含める
                    if entries:
                        entries.append(f"  {line}")
    return entries


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
        contact = request.POST.get('contact', '')
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
        contact_line = "\n返信先：" + contact if contact else ""
        message = "送信者：" + name + "\n" + "緊急度：" + emargency_level + "\n" + "ジャンル：" + genre + contact_line + "\n" + "詳細：" + detail

        #送信先取得
        email_json_path = os.path.join(settings.BASE_DIR, 'static', 'email.json')
        if os.path.exists(email_json_path):
            with open(email_json_path) as email_file:
                email_info = json.load(email_file)
        else:
            context = {'error': 'email.json が見つかりません。管理画面からメール設定を行ってください。'}
            return render(self.request, self.template_name, context)

        #メール送信（過去24時間のログを.logファイルとして添付）
        email = EmailMessage(
            subject='route294(清掃指示書作成支援システム)からのレポート',
            body=message,
            from_email=email_info['address'],
            to=[email_info['developer_address']],
        )

        recent_logs = _collect_recent_logs(hours=24)
        if recent_logs:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_content = "\n".join(recent_logs)
            email.attach(f"route294_logs_{now_str}.log", log_content, "text/plain")

        email.send(fail_silently=False)
        context = {}
        return redirect('/?from_report=1')
