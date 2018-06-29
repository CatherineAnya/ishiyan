from django.db import models


# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=100, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=100, verbose_name='密码')
    email = models.CharField(max_length=100, verbose_name='邮箱地址')
    phone = models.CharField(max_length=11, verbose_name='手机号码')
    status = models.CharField(max_length=100, verbose_name='工作状态')
    job_or_school = models.CharField(max_length=100, verbose_name='学校或工作')
    date = models.DateField(auto_now=True, verbose_name='注册时间')
    lab_num = models.IntegerField(default=0, verbose_name='实验次数')
    learn_minutes = models.IntegerField(default=0, verbose_name='累计实验时间')

    class Meta:
        verbose_name_plural = verbose_name = '用户'


class Label(models.Model):
    lid = models.AutoField(primary_key=True, verbose_name='标签ID')
    name = models.CharField(max_length=100, unique=True, verbose_name='标签名')

    class Meta:
        verbose_name_plural = verbose_name = '标签'


class Course(models.Model):
    cid = models.AutoField(primary_key=True, verbose_name='课程ID')
    name = models.CharField(max_length=200, unique=True, verbose_name='课程名')
    image = models.CharField(max_length=200, unique=True, verbose_name='课程图片')
    description = models.CharField(max_length=1024, verbose_name='课程描述')
    label = models.ForeignKey(Label, on_delete=models.CASCADE, verbose_name='课程标签')

    class Meta:
        verbose_name_plural = verbose_name = '课程'


class Upload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='上传课程')
    datetime = models.DateTimeField(auto_now=True, verbose_name='上传时间')

    class Meta:
        verbose_name_plural = verbose_name = '课程上传'


class Lab(models.Model):
    did = models.AutoField(primary_key=True, verbose_name='实验ID')
    name = models.CharField(max_length=100, verbose_name='实验名')
    content = models.CharField(max_length=200, unique=True, verbose_name='实验内容')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程')

    class Meta:
        verbose_name_plural = verbose_name = '实验'


class Learn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='学习用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='学习课程')
    last_lab = models.ForeignKey(Lab, on_delete=models.CASCADE, verbose_name='最后学习实验')
    datetime = models.DateTimeField(auto_now=True, verbose_name='学习时间')

    class Meta:
        verbose_name_plural = verbose_name = '学习记录'


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    message = models.CharField(max_length=1024, verbose_name='消息内容')
    datetime = models.DateTimeField(auto_now=True, verbose_name='消息时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    type = models.CharField(max_length=20, verbose_name='消息类型')

    class Meta:
        verbose_name_plural = verbose_name = '消息'


class Node(models.Model):
    name = models.CharField(max_length=30, verbose_name='节点名称')

    class Meta:
        verbose_name_plural = verbose_name = '帖子节点'


class Publish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发帖用户')
    title = models.CharField(max_length=100, verbose_name='帖子标题')
    content = models.CharField(max_length=1024, verbose_name='发帖内容')
    publish_datetime = models.DateTimeField(verbose_name='发帖时间')
    replay_datetime = models.DateTimeField(verbose_name='最新回帖时间')
    node = models.ForeignKey(Node, on_delete=models.CASCADE, verbose_name='所属节点')
    replay_num = models.IntegerField(default=0, verbose_name='回帖次数')
    view_num = models.IntegerField(default=0, verbose_name='查看次数')

    class Meta:
        verbose_name_plural = verbose_name = '发帖'


class Replay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='回帖用户')
    content = models.CharField(max_length=1024, verbose_name='回帖内容')
    datetime = models.DateTimeField(auto_now=True, verbose_name='回帖时间')
    publish = models.ForeignKey(Publish, on_delete=models.CASCADE, verbose_name='所属帖子')

    class Meta:
        verbose_name_plural = verbose_name = '回帖'


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='所属课程')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, verbose_name='所属实验')
    content = models.CharField(max_length=1024, verbose_name='报告内容')
    datetime = models.DateTimeField(auto_now=True, verbose_name='提交时间')

    class Meta:
        verbose_name_plural = verbose_name = '实验报告'

