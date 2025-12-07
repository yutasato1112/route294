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
from cleaning.views import sidewind as sidewind_view
from cleaning.views import release as release_view
from cleaning.views import tech as tech_view
from cleaning.views import administrator as admin_view
from cleaning.views import sidewind_front
from cleaning.views import rooming_list as rooming_list_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view.homeView.as_view(), name='home'),
    path('preview/', preview_view.previewView.as_view(), name='preview'),
    path('download/json/', json_view.download_json, name='download_json'),
    path('report/', report_view.reportView.as_view(), name='report'),
    path('sidewind/', sidewind_view.sidewindView.as_view(), name='sidewind'),
    path('release/', release_view.releaseView.as_view(), name='release'),
    path('technology/', tech_view.techView.as_view(), name='tech'),
    path('administrator/', admin_view.administratorView.as_view(), name='administrator'),
    path('logout/', admin_view.logout_view, name='logout'),
    path('sidewind_front/', sidewind_front.sidewind_front, name='sidewind_front'),
    path('rooming_list/', rooming_list_view.roomingListView.as_view(), name='rooming_list'),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
