from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # すでにログイン済みの場合は管理画面へリダイレクト
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('administrator')

        context = {}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # 認証
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            # ログイン成功
            login(request, user)

            # next パラメータがあればそちらへ、なければ管理画面へ
            next_url = request.GET.get('next', 'administrator')
            return redirect(next_url)
        else:
            # ログイン失敗
            context = {
                'error': 'ユーザー名またはパスワードが正しくありません。',
                'username': username
            }
            return render(request, self.template_name, context)
