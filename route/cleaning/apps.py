from django.apps import AppConfig
import os
import threading


def _save_startup_draft():
    """起動時に前日ログをGmail下書きに保存する"""
    import socket
    import imaplib
    import json
    import time
    import datetime
    import re
    from email.mime.text import MIMEText
    from pathlib import Path

    # インターネット接続確認
    try:
        socket.create_connection(('imap.gmail.com', 993), timeout=5)
    except OSError:
        return  # 接続不可の場合はスキップ

    # email.json 読み込み
    email_json_path = os.path.join('static', 'email.json')
    if not os.path.exists(email_json_path):
        return
    with open(email_json_path, encoding='utf-8') as f:
        email_info = json.load(f)
    address = email_info.get('address', '')
    password = email_info.get('password', '')
    if not address or not password:
        return

    # バージョン・起動日時
    from django.conf import settings
    version = getattr(settings, 'APP_VERSION', '不明')
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 前日ログ読み込み
    yesterday = (now.date() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    base_dir = Path(__file__).resolve().parent.parent
    log_path = base_dir / 'logs' / f'log_{yesterday}.log'
    if log_path.exists():
        log_content = log_path.read_text(encoding='utf-8', errors='ignore')
    else:
        log_content = '(前日のログファイルが見つかりません)'

    # メール本文作成
    body = (
        f'■ 起動日時: {now_str}\n'
        f'■ バージョン: ver.{version}\n\n'
        f'--- 前日 ({yesterday}) のログ ---\n\n'
        f'{log_content}'
    )

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = address
    msg['To'] = address
    msg['Subject'] = f'[route294] 起動ログ {now_str}'

    # Gmail 下書きフォルダに保存 (IMAP APPEND)
    try:
        with imaplib.IMAP4_SSL('imap.gmail.com', 993) as imap:
            imap.login(address, password)

            # \Drafts 属性を持つフォルダ名を取得
            drafts_folder = None
            status, mailboxes = imap.list()
            if status == 'OK':
                for mb in mailboxes:
                    if mb is None:
                        continue
                    mb_str = mb.decode('utf-8', errors='ignore') if isinstance(mb, bytes) else str(mb)
                    if '\\Drafts' in mb_str:
                        m = re.search(r'"([^"]+)"\s*$', mb_str)
                        if not m:
                            m = re.search(r'\s(\S+)\s*$', mb_str)
                        if m:
                            drafts_folder = m.group(1).strip('"')
                            break

            if drafts_folder is None:
                drafts_folder = '[Gmail]/Drafts'

            imap.append(
                f'"{drafts_folder}"',
                '\\Draft',
                imaplib.Time2Internaldate(time.time()),
                msg.as_bytes()
            )
    except Exception:
        pass  # 失敗しても起動を妨げない


class CleaningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cleaning'

    def ready(self):
        import sys
        # runserver の自動リロード時、親プロセス(ファイル監視)での二重実行を防ぐ
        # RUN_MAIN=true が子プロセス(実際のサーバー)を示す
        if 'runserver' in sys.argv and not os.environ.get('RUN_MAIN'):
            return
        t = threading.Thread(target=_save_startup_draft, daemon=True)
        t.start()
