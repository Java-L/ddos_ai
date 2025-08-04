from django.db import models
from datetime import datetime

from django.utils.html import escape


class User(models.Model):
    username = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=100)  # Password
    password_salt = models.CharField(max_length=50)  # Password salt
    status = models.IntegerField(default=1)  # 1=Normal 2=Disabled 6=Admin 9=Deleted
    create_at = models.DateTimeField(default=datetime.now)
    update_at = models.DateTimeField(default=datetime.now)
    is_authorize = models.BooleanField(default=False)
    is_change_file_type = models.BooleanField(default=False)  # Default generated file type is PDF

    def toDict(self):
        return {'id': self.id, 'username': self.username, 'nickname': self.nickname,
                'password_hash': self.password_hash, 'password_salt': self.password_salt, 'status': self.status,
                'create_at': self.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                'update_at': self.update_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_authorize': self.is_authorize}

    class Meta:
        db_table = 'user'


class Task(models.Model):
    # For storing scan tasks
    task_id = models.UUIDField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records')
    temp_result_file_path = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=True, blank=True)
    exec_time = models.CharField(null=True, blank=False, max_length=64)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')

    class Meta:
        db_table = 'records'


class TuningModels(models.Model):
    # 存储调优参数
    tuning_id = models.UUIDField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tuning_model_user')
    tuning_model = models.CharField(max_length=64, null=False, blank=False, verbose_name='调优模型')
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=True, blank=True)

    # User-set tuning parameters
    lr = models.FloatField(null=False, blank=False, verbose_name='Learning Rate')
    wd = models.FloatField(null=False, blank=False, verbose_name='Weight Decay')
    batch_size = models.IntegerField(null=False, blank=False, verbose_name='Batch Size')
    num_epochs = models.IntegerField(null=False, blank=False, verbose_name='Number of Epochs')
    accuracy = models.FloatField(null=True, blank=False, verbose_name='Accuracy')
    precision1 = models.FloatField(null=True, blank=False, verbose_name='Precision1')

    # Training results
    recall = models.FloatField(null=True, blank=True, verbose_name='Recall')
    f1 = models.FloatField(null=True, blank=True, verbose_name='F1 Score')
    # Creation time
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        db_table = 'tuning_models'


class IPAddressRule(models.Model):
    IP_RULE_CHOICES = [
        ('white', 'Whitelist'),
        ('black', 'Blacklist')
    ]

    ip_address = models.CharField(max_length=100, unique=True)
    rule_type = models.CharField(max_length=20, choices=IP_RULE_CHOICES)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 更新数据会自动更新时间

    def __str__(self):
        return f"{self.rule_type}: {self.ip_address}"


class TrafficLog(models.Model):
    """流量日志模型"""
    src_ip = models.CharField(max_length=255, verbose_name='源IP地址')
    dst_ip = models.CharField(max_length=255, verbose_name='目标IP地址')
    src_port = models.CharField(max_length=255, verbose_name='源端口')
    dst_port = models.CharField(max_length=255, verbose_name='目标端口')
    protocol = models.CharField(max_length=255, verbose_name='协议')
    features = models.TextField(verbose_name='特征内容')
    create_time = models.DateTimeField(verbose_name='创建时间')
    attack_type = models.CharField(max_length=255, null=True, blank=True, verbose_name='攻击类型')
    threat = models.CharField(max_length=255, null=True, blank=True, verbose_name='威胁级别')

    class Meta:
        verbose_name = '流量日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        db_table = 'tb_packetbaseinfo'

    def __str__(self):
        return f"{self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}"

