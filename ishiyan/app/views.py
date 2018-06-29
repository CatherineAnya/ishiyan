import os
import time
import json
import math
import base64
import random
import socket
import smtplib
import datetime
import markdown
import subprocess
from xml.etree.ElementTree import parse, Element
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from email.header import Header
from email.mime.text import MIMEText
import django.utils.timezone
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from app import models
from app.algorithm.levenshtein import levenshtein
from ishiyan import settings


pdfmetrics.registerFont(TTFont('yh', os.path.join(settings.STATIC_ROOT, 'msyh.ttf')))
DEFAULT_FONT['helvetica'] = 'yh'


# Create your views here.
def home(request):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    return render(request, 'index.html', {
        'title': '首页',
        'recommend_list': models.Course.objects.all().order_by('cid')[:4],
        'recently_list': models.Course.objects.all().order_by('cid')[4:12],
        'basic_list': models.Course.objects.filter(name__regex='.*入门*')[:4],
        'frontend_list': models.Course.objects.filter(label__name='Web').order_by('cid')[:4],
        'backend_list': models.Course.objects.filter(label__name='Python').order_by('cid')[:7],
        'cloudbig_list': models.Course.objects.filter(label__name__in=['Hadoop', 'R', 'Spark', '机器学习']).order_by('cid')[:10],
        'user': user,
    })


def login(request):
    if request.session.get('is_login', None):
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        return render(request, 'login.html', {
            'title': '登录'
        })
    else:
        response = {
            'message': '',
            'success': False,
        }
        username = request.POST['usr']
        password = request.POST['pwd']
        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            response['message'] = '用户名不存在'
        else:
            if user.password != password:
                response['message'] = '密码错误'
            else:
                response['success'] = True
                request.session['is_login'] = True
                request.session['username'] = username
        return HttpResponse(json.dumps(response), content_type='application/json')


def signup(request):
    if request.session.get('is_login', None):
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'title': '注册'
        })
    else:
        response = {
            'message': '',
            'success': False,
        }
        username = request.POST['usr']
        password = request.POST['pwd']
        email = request.POST['email']
        phone = request.POST['phone']
        verify = request.POST['verify']
        if verify != request.session.get('mail_code', None):
            response['message'] = '邮箱验证码错误'
            return HttpResponse(json.dumps(response), content_type='application/json')
        try:
            models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = models.User(username=username, password=password, email=email, phone=phone)
            user.save()
            response['success'] = True
            request.session['is_login'] = True
            request.session['username'] = username
            message = models.Message(user=user, message='欢迎使用在线实验平台，祝你学习进步！', type='站内公告')
            message.save()
        else:
            response['message'] = '用户名已存在'
        return HttpResponse(json.dumps(response), content_type='application/json')


def check_login(request):
    return HttpResponse(json.dumps({'login': request.session.get('is_login', False)}), content_type='application/json')


def logout(request):
    port = request.session.get('port', None)
    if port:
        subprocess.run(['vncserver', '-kill', ':' + str(int(port) - 5900)])
        doc = parse('/etc/guacamole/user-mapping.xml')
        root = doc.getroot()
        for authorize in root.iterfind('authorize'):
            if authorize.attrib['username'] == port:
                root.remove(authorize)
                break
        doc.write('/etc/guacamole/user-mapping.xml')
        request.session.flush()
    return HttpResponseRedirect('/')


def courses(request):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    page = int(request.GET.get('page', '1'))
    tag = request.GET.get('tag', None)
    query = request.GET.get('query', None)
    if tag and tag != 'all':
        allcourses_list = models.Course.objects.filter(label_id=models.Label.objects.get(name=tag).lid)
    else:
        allcourses_list = models.Course.objects.all()
    if query:
        tmp = {}
        for course in allcourses_list:
            tmp[course.name] = levenshtein(course.name, query) / len(course.name)
        allcourses_list = filter(lambda course: tmp[course.name] != 1, allcourses_list)
        allcourses_list = sorted(allcourses_list, key=lambda course: tmp[course.name])
    total_page = math.ceil(len(allcourses_list) / 16)
    allcourses_list = allcourses_list[(page - 1) * 16:page * 16]
    return render(request, 'courses.html', {
        'title': '课程',
        'alllabel_list': models.Label.objects.all(),
        'allcourses_list': allcourses_list,
        'total_page': total_page,
        'user': user,
    })


def course(request, cid):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    c = models.Course.objects.get(cid=cid)
    lab_list = models.Lab.objects.filter(course_id=c.cid)
    related_list = list(models.Course.objects.filter(label=c.label))
    try:
        uploader = models.Upload.objects.get(course_id=cid)
    except ObjectDoesNotExist:
        uploader = models.Upload(user=models.User(username='unknown'), datetime=datetime.datetime.now().strftime('%Y-%m-%d'))
    uploader = {
        'name': uploader.user.username,
        'total': len(models.Upload.objects.filter(user__username=uploader.user.username)),
        'upload_datetime': uploader.datetime,
    }
    return render(request, 'course.html', {
        'title': c.name,
        'user': user,
        'course': c,
        'lab_list': lab_list,
        'related_list': random.sample(related_list, min(8, len(related_list))),
        'uploader': uploader,
    })


def message(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    message_list = models.Message.objects.filter(user=user)
    return render(request, 'message.html', {
        'title': '消息中心',
        'user': user,
        'message_list': message_list,
    })


def account(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    if request.method == 'GET':
        return render(request, 'account.html', {
            'title': '账号管理',
            'user': user,
        })
    else:
        response = {
            'success': False,
            'message': ''
        }
        if request.POST['old-password'] or request.POST['new-password']:
            if user.password != request.POST['old-password']:
                response['message'] = '原密码错误'
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                user.password = request.POST['new-password']
        user.phone = request.POST['telephone']
        user.email = request.POST['email']
        user.save()
        response['success'] = True
        response['message'] = '保存成功'
        return HttpResponse(json.dumps(response), content_type='application/json')


def profile(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    if request.method == 'GET':
        return render(request, 'profile.html', {
            'title': '个人设置',
            'user': user,
        })
    else:
        response = {
            'success': False,
            'message': '',
        }
        user.username = request.POST['name']
        if request.POST['job_stat_code'] == '在上学':
            user.job_or_school = request.POST['school']
        else:
            user.job_or_school = request.POST['job']
        user.save()
        response['success'] = True
        response['message'] = '保存成功！'
        request.session['username'] = request.POST['name']
        return HttpResponse(json.dumps(response), content_type='application/json')


def homepage(request, uid):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    other = models.User.objects.get(uid=uid)
    learned = models.Learn.objects.filter(user=other)
    return render(request, 'homepage.html', {
        'title': '我的主页',
        'user': user,
        'other': other,
        'learn_course_list': learned,
        'learn_count': len(learned),
    })


def uploaded(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    uploaded = models.Upload.objects.filter(user=user)
    return render(request, 'uploaded.html', {
        'title': '我的主页',
        'user': user,
        'uploaded_course_list': uploaded,
        'upload_count': len(uploaded),
    })


def learned(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    page = int(request.GET.get('page', '1'))
    learned = models.Learn.objects.filter(user=user)[(page - 1) * 5:page * 5]
    total_page = math.ceil(len(models.Publish.objects.filter(user=user)) / 5)
    return render(request, 'learned.html', {
        'title': '已学课程',
        'user': user,
        'learn_course_list': learned,
        'learn_count': len(learned),
        'total_page': total_page,
    })


def upload(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    return render(request, 'upload.html', {
        'title': '上传课程',
        'user': user,
    })


def submit_report(request):
    response = {
        'success': False,
        'message': '',
    }
    if not request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    cid = request.POST['cid']
    did = request.POST['did']
    username = request.session['username']
    course = models.Course.objects.get(cid=cid)
    lab = models.Lab.objects.get(did=did)
    user = models.User.objects.get(username=username)
    content = request.POST['test-editormd-markdown-doc']
    try:
        report = models.Report.objects.get(user=user, course=course, lab=lab)
    except ObjectDoesNotExist:
        report = models.Report(user=user, course=course, lab=lab)
    report.content = content
    report.save()
    response['success'] = True
    response['message'] = '保存于' + str(datetime.datetime.now())
    return HttpResponse(json.dumps(response), content_type='application/json')


def report(request):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    user = models.User.objects.get(username=request.session['username'])
    page = int(request.GET.get('page', '1'))
    report_list = models.Report.objects.filter(user=user)[(page - 1) * 5:page * 5]
    total_page = math.ceil(len(models.Report.objects.filter(user=user)) / 5)
    for report in report_list:
        report.content = markdown.markdown(report.content, extensions=['markdown.extensions.extra'])
    return render(request, 'report.html', {
        'title': '我的实验报告',
        'user': user,
        'report_list': report_list,
        'report_count': len(report_list),
        'total_page': total_page,
    })


def document(request, cid, did):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    lab = models.Lab.objects.get(did=did)
    md = open('statics/website/doc/' + lab.content, encoding='utf-8').read()
    md = md.replace('show: step', '')
    md = md.replace('version: 1.0', '')
    md = md.replace('enable_checker: true', '')
    html = markdown.markdown(md, extensions=['markdown.extensions.toc', 'markdown.extensions.extra'])
    return render(request, 'labdoc.html', {
        'title': lab.name,
        'user': models.User.objects.get(username=request.session['username']),
        'content': html,
        'lab': lab,
    })


def startlab(request, cid, did):
    if not request.session.get('is_login', None):
        return HttpResponseRedirect('/login/')
    lab = models.Lab.objects.get(did=did)
    user = models.User.objects.get(username=request.session['username'])
    course = models.Course.objects.get(cid=cid)
    try:
        learn = models.Learn.objects.get(user=user, course=course)
    except ObjectDoesNotExist:
        learn = models.Learn(user=user, course=course, last_lab=lab)
    else:
        if learn.last_lab.did < lab.did:
            learn.last_lab = lab
    learn.save()
    md = open('statics/website/doc/' + lab.content, encoding='utf-8').read()
    md = md.replace('show: step', '')
    md = md.replace('version: 1.0', '')
    md = md.replace('enable_checker: true', '')
    html = markdown.markdown(md, extensions=['markdown.extensions.toc', 'markdown.extensions.extra'])
    try:
        report = models.Report.objects.get(user=user, course=course, lab=lab)
    except ObjectDoesNotExist:
        report_content = '''|                   |                     |
| -------------- | ---------------- |
|    实验标题  |                     |
|       姓名      |                     |
|       日期      |     年  月  日  |

---

## 实验目的

## 实验内容

## 实验结果

## 实验总结

'''
    else:
        report_content = report.content
    try:
        next_lab = models.Lab.objects.get(course=course, did=lab.did + 1)
    except ObjectDoesNotExist:
        next_lab_id = None
    else:
        next_lab_id = next_lab.did
    share = {
        'user': user.username,
        'port': request.session['port']
    }
    return render(request, 'startlab.html', {
        'title': lab.name,
        'user': user,
        'content': html,
        'lab': lab,
        'next_lab_id': next_lab_id,
        'report_content': report_content,
        'port': request.session['port'],
        't': base64.b64encode(json.dumps(share).encode()).decode(),
    })


def discuss(request):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    node = request.GET.get('node', None)
    page = int(request.GET.get('page', '1'))
    order = request.GET.get('order', None)
    if order == '2':
        allpublishes = models.Publish.objects.all().order_by('-replay_datetime')
    elif order == '2':
        allpublishes = models.Publish.objects.all().order_by('-replay_num')
    else:
        allpublishes = models.Publish.objects.all().order_by('-publish_datetime')
    if node and node != 'all':
        allpublishes = allpublishes.filter(node_id=int(node))
    total_page = math.ceil(len(allpublishes) / 20)
    allpublishes = allpublishes[(page - 1) * 20:page * 20]
    return render(request, 'discuss.html', {
        'title': '讨论区',
        'user': user,
        'allnode_list': models.Node.objects.all(),
        'total_page': total_page,
        'publish_list': allpublishes,
    })


def send_mail(request):
    response = {
        'message': '',
        'success': False,
    }
    if request.method != 'GET':
        response['message'] = '非法请求'
        return HttpResponse(json.dumps(response), content_type='application/json')
    to_addrs = request.GET['email']
    code = random.randrange(100000, 999999)
    # 填充邮件信息
    content = MIMEText('尊敬的爱实验用户,您好：\n\n'
                       f'您正在爱实验进行邮箱注册的操作，本次请求的邮件验证码是：{code}\n\n'
                       '如非本人操作，请忽略该邮件。\n\n'
                       '祝在爱实验收获愉快！')
    content['From'] = Header('爱实验', 'utf-8')
    content['To'] = to_addrs
    content['Subject'] = Header('爱实验邮箱验证码', 'utf-8')
    # 连接SMTP服务器并发送邮件
    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('ishiyan100@outlook.com', 'q553500416')
        server.sendmail(from_addr='ishiyan100@outlook.com', to_addrs=to_addrs, msg=content.as_string())
        server.close()
    except Exception as ex:
        response['message'] = '发送失败'
    else:
        response['message'] = '发送成功'
        response['success'] = True
        request.session['mail_code'] = str(code)
    return HttpResponse(json.dumps(response), content_type='application/json')


def question(request, qid):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    publish = models.Publish.objects.get(id=qid)
    if request.method == 'GET':
        publish.view_num += 1
        publish.save()
        replay_list = models.Replay.objects.filter(publish=publish).order_by('datetime')
        return render(request, 'question.html', {
            'title': '讨论区',
            'user': user,
            'publish': publish,
            'replay_list': replay_list,
        })
    else:
        content = request.POST['test-editormd-html-code']
        replay = models.Replay(user=user, content=content, publish=publish)
        replay.save()
        publish.replay_num += 1
        publish.replay_datetime = django.utils.timezone.now()
        publish.save()
        return HttpResponseRedirect('/question/' + str(qid))


def publish(request):
    if request.session.get('is_login', None):
        user = models.User.objects.get(username=request.session['username'])
    else:
        user = None
    if request.method == 'GET':
        return render(request, 'publish.html', {
            'title': '我要发帖',
            'user': user,
            'node_list': models.Node.objects.all(),
        })
    else:
        title = request.POST['title']
        content_html = request.POST['test-editormd-html-code']
        node_id = request.POST['node-id']
        node = models.Node.objects.get(id=node_id)
        publish = models.Publish(user=user, title=title, content=content_html, node=node)
        publish.publish_datetime = publish.replay_datetime = django.utils.timezone.now()
        publish.save()
        return HttpResponseRedirect('/question/' + str(publish.id))


def delete_report(request):
    response = {
        'success': False,
        'message': '',
    }
    if request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    report_id = request.GET['report']
    try:
        report = models.Report.objects.get(id=report_id)
    except ObjectDoesNotExist:
        response['message'] = '该实验报告不存在'
    else:
        report.delete()
        response['success'] = True
        response['message'] = '删除成功'
    return HttpResponse(json.dumps(response), content_type='application/json')


def delete_learn(request):
    response = {
        'success': False,
        'message': '',
    }
    if request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    learn_id = request.GET['learn']
    try:
        learn = models.Learn.objects.get(id=learn_id)
    except ObjectDoesNotExist:
        response['message'] = '该学习记录不存在'
    else:
        learn.delete()
        response['success'] = True
        response['message'] = '删除成功'
    return HttpResponse(json.dumps(response), content_type='application/json')


def readonly(request):
    t = request.GET.get('t')
    if t:
        j = json.loads(base64.b64decode(t).decode())
        share_user = j['user']
        port = j['port']
    else:
        share_user, port = None, None
    return render(request, 'readonly.html', {
        'title': '只读模式',
        'share_user': share_user,
        'port': port,
    })


def cooperation(request):
    t = request.GET.get('t')
    if t:
        j = json.loads(base64.b64decode(t).decode())
        share_user = j['user']
        port = j['port']
    else:
        share_user, port = None, None
    return render(request, 'cooperation.html', {
        'title': '协作模式',
        'share_user': share_user,
        'port': port,
    })


def download_code(request):
    response = {
        'success': False,
        'message': '',
        'url': '',
    }
    if not request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    username = request.session['username']
    res = subprocess.run(['bash', os.path.join(settings.BASE_DIR, 'app', 'shell', 'download_code.sh'), username], stdout=subprocess.PIPE)
    if res.returncode == 0:
        response['success'] = True
        response['url'] = os.path.join(settings.STATIC_URL, 'downloads', 'code', username + '.zip')
    else:
        response['message'] = res.stdout.decode()
    return HttpResponse(json.dumps(response), content_type='application/json')


def download_report(request):
    if not request.session.get('is_login', None):
        return HttpResponse('下载失败，未登录')
    file_type = request.GET['type']
    report_id = request.GET['report_id']
    try:
        report = models.Report.objects.get(id=report_id)
    except ObjectDoesNotExist:
        return HttpResponse('下载失败，实验报告不存在')
    filename = str(report.user.uid) + '_' + str(report.course.cid) + '_' + str(report.lab.did)
    if file_type == 'markdown':
        content = report.content
        extension = '.md'
    elif file_type == 'html':
        content = markdown.markdown(report.content, extensions=['markdown.extensions.extra'])
        extension = '.html'
    elif file_type == 'pdf':
        extension = '.pdf'
        html = markdown.markdown(report.content, extensions=['markdown.extensions.extra'])
        print(html)
        file = open(os.path.join(settings.STATIC_ROOT, 'downloads', 'doc', filename + extension), 'wb')
        pisa.CreatePDF(html, dest=file)
        file.close()
        file = open(os.path.join(settings.STATIC_ROOT, 'downloads', 'doc', filename + extension), 'rb')
        response = HttpResponse(file.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename + extension)
        file.close()
        return response
    else:
        return HttpResponse('下载失败，文件类型不支持')
    response = HttpResponse(content, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename + extension)
    return response


def add_minutes(request):
    response = {
        'success': False,
        'message': '',
    }
    minutes = request.GET['minute']
    user = models.User.objects.get(username=request.session['username'])
    user.learn_minutes += minutes
    return HttpResponse(json.dumps(response), content_type='application/json')


def create_vnc(request):
    response = {
        'success': False,
        'message': '',
    }
    if not request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    if request.session.get('port', None):
        response['success'] = True
        response['message'] = '端口已分配'
        return HttpResponse(json.dumps(response), content_type='application/json')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for port in range(5901, 65536):
        try:
            s.bind(('127.0.0.1', port))
        except socket.error:
            pass
        else:
            s.close()
            time.sleep(1)
            subprocess.run(['vncserver', '-geometry', '900x800'])
            doc = parse('/etc/guacamole/user-mapping.xml')
            root = doc.getroot()
            authorize = Element('authorize', attrib={
                'password': str(port), 'username': str(port)
            })
            e = Element('protocol')
            e.text = 'vnc'
            authorize.append(e)
            e = Element('param', attrib={'name': 'hostname'})
            e.text = 'localhost'
            authorize.append(e)
            e = Element('param', attrib={'name': 'port'})
            e.text = str(port)
            authorize.append(e)
            e = Element('param', attrib={'name': 'password'})
            e.text = 'likexin'
            authorize.append(e)
            root.append(authorize)
            doc.write('/etc/guacamole/user-mapping.xml')
            response['success'] = True
            response['message'] = '分配成功'
            request.session['port'] = str(port)
            break
    return HttpResponse(json.dumps(response), content_type='application/json')


def stop_vnc(request):
    response = {
        'success': False,
        'message': '',
    }
    if not request.session.get('is_login', None):
        response['message'] = '未登录'
        return HttpResponse(json.dumps(response), content_type='application/json')
    if not request.session.get('port', None):
        response['message'] = '未分配端口'
        return HttpResponse(json.dumps(response), content_type='application/json')
    port = request.session['port']
    subprocess.run(['vncserver', '-kill', ':' + str(int(port) - 5900)])
    doc = parse('/etc/guacamole/user-mapping.xml')
    root = doc.getroot()
    for authorize in root.iterfind('authorize'):
        if authorize.attrib['username'] == port:
            root.remove(authorize)
            break
    doc.write('/etc/guacamole/user-mapping.xml')
    del request.session['port']

