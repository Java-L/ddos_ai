# -*- coding: utf-8 -*-
"""
中间件模块
包含登录验证和流量监控功能
"""

import time
import random
import threading
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.shortcuts import HttpResponse, redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from main.models import TrafficLog
import logging

logger = logging.getLogger(__name__)


class LoginRequiredMiddleware:

    def process_request(self, request):
        public_urls = [
            'myadmin_login',
            'myadmin_login2',
            'myadmin_do_login',
            'myadmin_register',
            'myadmin_do_register',
            'myadmin_logout',
            'forgot_pd',
            'captcha-image',

            # 其他公开访问的 URL...
        ]

        # 如果请求的路径是公开URL，则不进行登录检查
        current_url_name = resolve(request.path_info).url_name
        # print("访问的URL", current_url_name)
        if current_url_name in public_urls:
            # 调用视图
            return

        # 检查用户是否登录
        is_login = request.session.get('is_login', False)
        if is_login:
            # 用户已登录
            print("登录")
            return
        else:
            print("未登录")
            return redirect(reverse('myadmin_login2'))


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        public_urls = [
            'myadmin_login',
            'myadmin_login2',
            'myadmin_do_login',
            'myadmin_register',
            'myadmin_do_register',
            'myadmin_logout',
            'forgot_pd',
            'captcha-image',

            # 其他公开访问的 URL...
        ]
        current_url_name = resolve(request.path_info).url_name
        if current_url_name in public_urls:
            # print("在视图列表中")
            # 调用视图
            return
        else:
            is_login = request.session.get('is_login', False)
            # print(request.session.get('is_login'))
            # print(is_login)
            if is_login:
                return
                # 登录成功，将继续执行后续程序
            else:
                return redirect(reverse('myadmin_login2'))
