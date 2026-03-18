from django.apps import AppConfig
import os
import threading


def _save_startup_draft():
    """起動時に前日ログとworklogをGmail下書きに添付保存する"""
    import socket
    import imaplib
    import json
    import time
    import datetime
    import re
    import glob as glob_mod
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
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

    base_dir = Path(__file__).resolve().parent.parent

    # メール作成（マルチパート）
    msg = MIMEMultipart()
    msg['From'] = address
    msg['To'] = address
    msg['Subject'] = f'[route294] 起動ログ {now_str}'

    # 本文
    body = (
        f'■ 起動日時: {now_str}\n'
        f'■ バージョン: ver.{version}\n\n'
        f'添付ファイル:\n'
        f'  - 前日ログファイル (.log)\n'
        f'  - 直近のワークログ (.json)\n'
    )
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 前日ログをファイルとして添付
    yesterday = (now.date() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    log_path = base_dir / 'logs' / f'log_{yesterday}.log'
    if log_path.exists():
        log_content = log_path.read_bytes()
        log_attachment = MIMEBase('text', 'plain')
        log_attachment.set_payload(log_content)
        encoders.encode_base64(log_attachment)
        log_attachment.add_header(
            'Content-Disposition', 'attachment',
            filename=f'log_{yesterday}.log'
        )
        msg.attach(log_attachment)

    # 直近のworklogを添付
    media_dir = base_dir / 'media'
    if media_dir.exists():
        worklog_files = sorted(
            media_dir.glob('worklog_*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if worklog_files:
            latest_worklog = worklog_files[0]
            wl_content = latest_worklog.read_bytes()
            wl_attachment = MIMEBase('application', 'json')
            wl_attachment.set_payload(wl_content)
            encoders.encode_base64(wl_attachment)
            wl_attachment.add_header(
                'Content-Disposition', 'attachment',
                filename=latest_worklog.name
            )
            msg.attach(wl_attachment)

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
