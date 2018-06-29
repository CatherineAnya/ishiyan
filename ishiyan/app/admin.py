from django.contrib import admin
from app.models import User
from app.models import Label
from app.models import Course
from app.models import Upload
from app.models import Learn
from app.models import Lab
from app.models import Message
from app.models import Publish
from app.models import Node
from app.models import Replay
from app.models import Report

# Register your models here.
admin.site.register([
    User,
    Label,
    Course,
    Upload,
    Learn,
    Lab,
    Message,
    Publish,
    Node,
    Replay,
    Report,
])
admin.site.site_title = admin.site.site_header = '爱实验后台管理'
