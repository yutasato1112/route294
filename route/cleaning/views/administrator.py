import csv
import datetime
import re
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


MASTER_DIR = Path(settings.BASE_DIR) / "static" / "csv"
LOG_DIR = Path(settings.BASE_DIR) / "logs"


def _now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


@method_decorator(staff_member_required, name="dispatch")
class administratorView(TemplateView):
    template_name = "administrator.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("query", "").strip()
        context = super().get_context_data(**kwargs)
        context.update(
            master_data=_list_master_files(),
            logs=_list_logs(query),
            query=query,
            message=kwargs.get("message"),
        )
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        action = request.POST.get("action")
        message = None

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

        context = self.get_context_data(message=message)
        return render(request, self.template_name, context)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("home")
