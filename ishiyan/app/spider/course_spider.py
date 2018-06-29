import re
import uuid
import time
import requests

from django.core.exceptions import ObjectDoesNotExist
from app import models

def spider_login(session, username, password):
    response = session.get('https://www.shiyanlou.com')
    csrftoken = re.search(r'<meta name="csrf-token" content="(.*?)">', response.text)
    response = session.post(
        url='https://www.shiyanlou.com/login',
        data='login={}&password={}&remember='.format(username, password),
        headers={
            'X-CSRFToken': csrftoken[1],
        },
    )
    j = response.json()
    return j.get('ok', False)
def spid_it(session):
    for i in range(1, 10):
        response = session.get('https://www.shiyanlou.com/courses/?category=all&course_type=all&fee=free&tag=all&page=' + str(i))
        names = re.finditer(r'<div class="course-name">(.+?)</div>', response.text)
        descs = re.finditer(r'<div class="course-desc">(.+?)</div>', response.text)
        images = re.finditer(r'<img alt="(.+?)" src="(.+?)">', response.text)
        image_mapping = dict((image.group(1), image.group(2)) for image in images)
        courses_id = re.finditer(r'<a class="course-box" href="/courses/(\d+)">', response.text)
        counter = 0
        for name, desc, course_id in zip(names, descs, courses_id):
            flag = False
            response = session.get('https://www.shiyanlou.com/courses/{}'.format(course_id.group(1)))
            label = re.search(r'data-course-tag="(.+?)"', response.text)
            if not label:
                continue
            label = label.group(1).split(',')[0]
            labs_id = re.finditer(r'<span class="lab-id" data-lab-id="(\d+)">', response.text)
            labs_name = re.finditer(r'<div class="lab-item-title" title=".+?">(.+?)</div>', response.text)
            for lab_id, lab_name in zip(labs_id, labs_name):
                response = session.get('https://www.shiyanlou.com/courses/{}/labs/{}/document'.format(course_id.group(1), lab_id.group(1)), headers={'Referer': response.url})
                doc_uri = re.search(r'data-courses-doc="(.+?)"', response.text)
                if not doc_uri:
                    continue
                doc_json = session.get('https://www.shiyanlou.com' + doc_uri.group(1), headers={'Referer': response.url}).json()
                if not doc_json['document']:
                    continue
                if not flag:
                    try:
                        l = models.Label.objects.get(name=label)
                    except ObjectDoesNotExist:
                        l = models.Label(name=label)
                        l.save()
                    file_name = str(uuid.uuid4().int % 1000000000) + '.jpg'
                    with open('statics/website/img/course/' + file_name, 'wb') as fd:
                        fd.write(requests.get(image_mapping[name.group(1)]).content)
                    course = models.Course(
                        name=name.group(1),
                        image=file_name,
                        description=desc.group(1),
                        label=l,
                    )
                    course.save()
                    flag = True
                course = models.Course.objects.get(name=name.group(1))
                file_name = str(uuid.uuid4().int % 1000000000) + '.md'
                with open('statics/website/doc/' + file_name, 'w', encoding='utf-8') as fd:
                    fd.write(doc_json['document'])
                lab = models.Lab(
                    name=lab_name.group(1),
                    content=file_name,
                    course=course
                )
                lab.save()
                counter += 1
                print(counter)
                time.sleep(2.5)
def spider():
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.headers.update({
        'Origin': 'https://www.shiyanlou.com',
        'Referer': 'https://www.shiyanlou.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Encoding': 'gzip, deflate, br',
    })
    spider_login(session, '1758887886@qq.com', 'q553500416')
    spid_it(session)
