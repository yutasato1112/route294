import csv
import datetime
import json
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from functools import wraps


MASTER_DIR = Path(settings.BASE_DIR) / "static" / "csv"
LOG_DIR = Path(settings.BASE_DIR) / "logs"
SETTINGS_DIR = Path(settings.BASE_DIR) / "static"


def staff_required(view_func):
    """
    カスタムログイン画面を使用するスタッフ専用デコレータ
    """
    @wraps(view_func)
    @login_required(login_url='/login/')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("このページにアクセスする権限がありません。")
        return view_func(request, *args, **kwargs)
    return wrapper


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_json_setting(filename):
    """JSON設定ファイルを読み込む"""
    path = SETTINGS_DIR / filename
    if path.exists():
        try:
            with path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return None
    return None


def _save_json_setting(filename, data):
    """JSON設定ファイルを保存"""
    path = SETTINGS_DIR / filename
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _list_master_files():
    files = []
    for path in sorted(MASTER_DIR.glob("*.csv")):
        stat = path.stat()
        rows_preview = []
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i >= 20:
                        break
                    rows_preview.append(row)
        except Exception:
            rows_preview = []
        files.append(
            {
                "id": path.name,
                "name": path.name,
                "updated_at": datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "size": stat.st_size,
                "body": path.read_text(encoding="utf-8", errors="ignore"),
                "rows_preview": rows_preview,
            }
        )
    return files


def _list_logs(query: str = ""):
    entries = []
    if LOG_DIR.exists():
        for path in sorted(LOG_DIR.glob("log_*.log"), reverse=True):
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(\w+)\] (.*)$", line)
                    ts, level, msg = None, None, None
                    if m:
                        ts, level, msg = m.group(1), m.group(2), m.group(3)
                    else:
                        msg = line
                    if query and query.lower() not in line.lower():
                        continue
                    entries.append(
                        {
                            "file": path.name,
                            "timestamp": ts or "",
                            "level": level or "",
                            "message": msg,
                            "_sort_key": f"{path.name}-{ts or ''}",
                        }
                    )
    # sort by file (newest) then timestamp (desc)
    entries.sort(key=lambda x: x.get("_sort_key", ""), reverse=True)
    for e in entries:
        e.pop("_sort_key", None)
    return entries[:300]


def _list_users():
    """ユーザー一覧を取得"""
    users = []
    for user in User.objects.all().order_by('-date_joined'):
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email or '-',
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        })
    return users


@method_decorator(staff_required, name="dispatch")
class administratorView(TemplateView):
    template_name = "administrator.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("query", "").strip()
        context = super().get_context_data(**kwargs)

        logs = _list_logs(query)
        logs_json = json.dumps(logs, ensure_ascii=False)

        # 設定ファイル読み込み
        email_settings = _load_json_setting('email.json') or {}

        # ユーザー一覧
        users = _list_users()

        context.update(
            master_data=_list_master_files(),
            logs=logs,
            logs_json=logs_json,
            query=query,
            message=kwargs.get("message"),
            email_settings=email_settings,
            users=users,
            current_user=self.request.user,
        )
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        action = request.POST.get("action")
        message = None

        # Ajaxリクエストの判定
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        MASTER_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        if action == "create_master":
            name = request.POST.get("name", "").strip()
            body = request.POST.get("body", "")
            if not name.endswith(".csv"):
                name = f"{name}.csv"
            target = MASTER_DIR / name
            target.write_text(body, encoding="utf-8")
            message = "マスタデータを作成しました。"

        elif action == "update_master":
            master_id = request.POST.get("master_id")
            new_name = request.POST.get("name", master_id).strip()
            if not new_name.endswith(".csv"):
                new_name = f"{new_name}.csv"
            body = request.POST.get("body", "")
            src = MASTER_DIR / master_id
            dst = MASTER_DIR / new_name
            if src.exists():
                src.write_text(body, encoding="utf-8")
                if src.name != dst.name:
                    src.rename(dst)
                message = "マスタデータを更新しました。"

        elif action == "delete_master":
            master_id = request.POST.get("master_id")
            target = MASTER_DIR / master_id
            if target.exists():
                target.unlink()
                message = "マスタデータを削除しました。"

        elif action == "delete_logs":
            removed = 0
            for path in LOG_DIR.glob("log_*.log"):
                path.unlink(missing_ok=True)
                removed += 1
            message = f"ログファイルを削除しました（{removed}件）。"

        elif action == "update_email_settings":
            developer_address = request.POST.get("developer_address", "").strip()

            # バリデーション
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            errors = []

            if not re.match(email_pattern, developer_address):
                errors.append("開発者メールアドレスの形式が不正です")

            if errors:
                message = "エラー: " + " / ".join(errors)
                if is_ajax:
                    return JsonResponse({'success': False, 'message': message})
            else:
                # 既存の設定を読み込み、developer_addressのみ更新
                existing_data = _load_json_setting("email.json") or {}
                existing_data["developer_address"] = developer_address
                _save_json_setting("email.json", existing_data)
                message = "メール設定を更新しました"

        elif action == "change_password":
            current_password = request.POST.get("current_password", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            errors = []

            # バリデーション
            if not current_password:
                errors.append("現在のパスワードを入力してください")
            elif not request.user.check_password(current_password):
                errors.append("現在のパスワードが正しくありません")

            if not new_password:
                errors.append("新しいパスワードを入力してください")
            elif len(new_password) < 8:
                errors.append("パスワードは8文字以上で設定してください")

            if new_password != confirm_password:
                errors.append("新しいパスワードが一致しません")

            if errors:
                message = "エラー: " + " / ".join(errors)
                if is_ajax:
                    return JsonResponse({'success': False, 'message': message})
            else:
                # パスワード変更
                request.user.set_password(new_password)
                request.user.save()
                # セッションを維持（ログアウトしないようにする）
                update_session_auth_hash(request, request.user)
                message = "パスワードを変更しました"

        elif action == "create_user":
            # スーパーユーザーのみ実行可能
            if not request.user.is_superuser:
                message = "エラー: 権限がありません"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': message})
            else:
                username = request.POST.get("username", "").strip()
                password = request.POST.get("password", "").strip()
                email = request.POST.get("email", "").strip()
                is_staff = request.POST.get("is_staff") == "on"
                is_superuser = request.POST.get("is_superuser") == "on"

                errors = []

                # バリデーション
                if not username:
                    errors.append("ユーザー名を入力してください")
                elif User.objects.filter(username=username).exists():
                    errors.append("このユーザー名は既に使用されています")

                if not password:
                    errors.append("パスワードを入力してください")
                elif len(password) < 8:
                    errors.append("パスワードは8文字以上で設定してください")

                if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    errors.append("メールアドレスの形式が不正です")

                if errors:
                    message = "エラー: " + " / ".join(errors)
                    if is_ajax:
                        return JsonResponse({'success': False, 'message': message})
                else:
                    # ユーザー作成
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        is_staff=is_staff
                    )
                    # スーパーユーザー権限を設定
                    if is_superuser:
                        user.is_superuser = True
                        user.save()
                    message = f"ユーザー「{username}」を作成しました"

        elif action == "delete_user":
            # スーパーユーザーのみ実行可能
            if not request.user.is_superuser:
                message = "エラー: 権限がありません"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': message})
            else:
                user_id = request.POST.get("user_id")
                try:
                    user = User.objects.get(id=user_id)
                    # 自分自身は削除できない
                    if user.id == request.user.id:
                        message = "エラー: 自分自身を削除することはできません"
                        if is_ajax:
                            return JsonResponse({'success': False, 'message': message})
                    else:
                        username = user.username
                        user.delete()
                        message = f"ユーザー「{username}」を削除しました"
                except User.DoesNotExist:
                    message = "エラー: ユーザーが見つかりません"
                    if is_ajax:
                        return JsonResponse({'success': False, 'message': message})

        # レスポンス返却
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': message
            })
        else:
            context = self.get_context_data(message=message)
            return render(request, self.template_name, context)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("home")


@staff_required
def get_csv_view(request: HttpRequest):
    """
    CSVファイルの内容を取得してJSON形式で返す
    """
    filename = request.GET.get('filename')

    if not filename:
        return JsonResponse({'error': 'ファイル名が指定されていません'}, status=400)

    path = MASTER_DIR / filename

    if not path.exists():
        return JsonResponse({'error': 'ファイルが見つかりません'}, status=404)

    # セキュリティチェック: パストラバーサル対策
    if not str(path.resolve()).startswith(str(MASTER_DIR.resolve())):
        return JsonResponse({'error': '不正なファイルパスです'}, status=403)

    try:
        with path.open('r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        return JsonResponse({
            'filename': filename,
            'data': rows
        })
    except Exception as e:
        return JsonResponse({'error': f'ファイルの読み込みに失敗しました: {str(e)}'}, status=500)
