"""ishiyan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from app import views

urlpatterns = [
    path(r'', views.home),
    path(r'login/', views.login),
    path(r'check_login/', views.check_login),
    path(r'signup/', views.signup),
    path(r'logout/', views.logout),
    path(r'courses/', views.courses),
    path(r'course/<int:cid>/', views.course),
    path(r'message/', views.message),
    path(r'profile/', views.profile),
    path(r'account/', views.account),
    path(r'homepage/<int:uid>', views.homepage),
    path(r'uploaded/', views.uploaded),
    path(r'learned/', views.learned),
    path(r'upload/', views.upload),
    path(r'report/', views.report),
    path(r'course/<int:cid>/document/<int:did>', views.document),
    path(r'course/<int:cid>/startlab/<int:did>', views.startlab),
    path(r'discuss/', views.discuss),
    path(r'question/<int:qid>', views.question),
    path(r'publish/', views.publish),
    path(r'submit_report/', views.submit_report),
    path(r'delete_report/', views.delete_report),
    path(r'delete_learn/', views.delete_learn),
    path(r'readonly/', views.readonly),
    path(r'cooperation/', views.cooperation),
    path(r'send_mail/', views.send_mail),
    path(r'download_code/', views.download_code),
    path(r'download_report/', views.download_report),
    path(r'add_minutes/', views.add_minutes),
    path(r'create_vnc/', views.create_vnc),
    path(r'stop_vnc/', views.stop_vnc),
    path(r'admin/', admin.site.urls),
]