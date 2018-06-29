import re
import random
import requests
import django.utils.timezone

from app import models

for page in range(2, 20):
    response = requests.get(f'https://www.nowcoder.com/discuss?type=1&order=0&page={page}')
    discuss = re.finditer(r'/discuss/(\d+)\?', response.text)
    for discuss_id in discuss:
        response = requests.get(f'https://www.nowcoder.com/discuss/{discuss_id.group(1)}')
        title = re.search(r'<h1 class="discuss-title">(.+?)\n', response.text).group(1)
        content = re.search(r'<div class="post-topic-des">(.+?)</div>\n<div class="clearfix">', response.text, re.DOTALL).group(1)
        author = re.search(r'作者：(.+?)"', response.text).group(1)
        if '牛客' in title or '牛客' in content or '牛客' in author:
            continue
        try:
            user = models.User.objects.get(username=author)
        except Exception as ex:
            user = models.User(username=author, password='123456789', email=str(random.randrange(1000000000, 9999999999)) + '@qq.com')
            user.save()
        node = models.Node.objects.get(name='交流讨论')
        publish = models.Publish(user=user, title=title, content=content, node=node)
        publish.publish_datetime = publish.replay_datetime = django.utils.timezone.now()
        publish.view_num = random.randrange(50, 150)
        publish.save()
        response = requests.get(f'https://www.nowcoder.com/comment/list-by-page-v2?token=&pageSize=20&page=1&order=1&entityId={discuss_id.group(1)}&entityType=8&_=1528295757359')
        json = response.json()
        for replay in json['data']['comments']:
            authorName = replay['authorName']
            try:
                user = models.User.objects.get(username=authorName)
            except Exception as ex:
                user = models.User(username=authorName, password='123456789', email=str(random.randrange(1000000000, 9999999999)) + '@qq.com')
                user.save()
            content = replay['content']
            if '牛客' in content:
                continue
            replay = models.Replay(user=user, content=content, publish=publish)
            replay.save()
            publish.replay_num += 1
            publish.save()
