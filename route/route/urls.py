"""
URL configuration for route project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static
from cleaning.views import home as home_view
from cleaning.views import preview as preview_view
from cleaning.views import download_json as json_view
from cleaning.views import report as report_view
from cleaning.views import ai_assist as ai_assist_view
from cleaning.views import release as release_view
from cleaning.views import tech as tech_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view.homeView.as_view(), name='home'),
    path('preview/', preview_view.previewView.as_view(), name='preview'),
    path('download/json/', json_view.download_json, name='download_json'),
    path('report/', report_view.reportView.as_view(), name='report'),
    path('ai_assist/', ai_assist_view.aiAssistView.as_view(), name='ai_assist'),
    path('release/', release_view.releaseView.as_view(), name='release'),
    path('technology/', tech_view.techView.as_view(), name='tech'),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)