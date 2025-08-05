from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from .models import User
import hashlib
import random


def index(request, pIndex=1):
    """用户列表"""
    try:
        # 获取用户列表
        ulist = User.objects.filter(status__lt=9)

        # 搜索处理
        mywhere = []
        kw = request.GET.get("keyword", None)
        if kw:
            ulist = ulist.filter(Q(username__contains=kw) | Q(nickname__contains=kw))
            mywhere.append('keyword=' + kw)

        # 分页处理
        pIndex = int(pIndex)
        page = Paginator(ulist, 50)
        maxPages = page.num_pages
        pIndex = min(max(pIndex, 1), maxPages)
        list2 = page.page(pIndex)
        plist = page.page_range

        context = {
            "userlist": list2,
            'plist': plist,
            'pIndex': pIndex,
            'maxPages': maxPages,
            'mywhere': mywhere,
            'keyword': kw
        }
        return render(request, 'myadmin/user/index.html', context)
    except Exception as e:
        print(f"Error getting user list: {str(e)}")
        messages.error(request, 'Failed to get user list')
        return render(request, 'myadmin/user/index.html', {'userlist': []})


def insert(request):
    """Add user / 添加用户"""
    try:
        if request.method == "POST":
            ob = User()
            ob.username = request.POST['username']
            ob.nickname = request.POST['nickname']

            # Password encryption processing / 密码加密处理
            md5 = hashlib.md5()
            n = random.randint(100000, 999999)
            s = request.POST['password'] + str(n)
            md5.update(s.encode('utf-8'))
            ob.password_hash = md5.hexdigest()
            ob.password_salt = n

            ob.status = int(request.POST.get('status', 1))
            ob.create_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ob.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ob.save()

            messages.success(request, 'User added successfully')
            return redirect('myadmin_user_index', 1)
    except Exception as err:
        print(f"Error adding user: {str(err)}")
        messages.error(request, 'Failed to add user')
    return redirect('myadmin_user_index', 1)


def delete(request, uid=0):
    """Delete user / 删除用户"""
    try:
        ob = User.objects.get(id=uid)
        ob.status = 9
        ob.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ob.save()
        messages.success(request, 'User deleted successfully')
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        messages.error(request, 'Failed to delete user')
    return redirect('myadmin_user_index', 1)


def edit(request, uid=0):
    """Edit user / 编辑用户"""
    try:
        user = User.objects.get(id=uid)
        if request.method == 'POST':
            user.username = request.POST.get('username', user.username)
            user.nickname = request.POST.get('nickname', user.nickname)

            # Update if new password is provided / 如果提供了新密码则更新
            if password := request.POST.get('password'):
                md5 = hashlib.md5()
                n = random.randint(100000, 999999)
                s = password + str(n)
                md5.update(s.encode('utf-8'))
                user.password_hash = md5.hexdigest()
                user.password_salt = n

            user.status = int(request.POST.get('status', user.status))
            user.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user.save()
            messages.success(request, 'User updated successfully')
            return redirect('myadmin_user_index', 1)

        return render(request, 'myadmin/user/edit.html', {'user': user})
    except Exception as err:
        print(f"Error editing user: {str(err)}")
        messages.error(request, 'Failed to edit user')
        return redirect('myadmin_user_index', 1)


def update(request, uid):
    """Toggle user status / 切换用户状态"""
    try:
        user = User.objects.get(id=uid)
        user.status = 2 if user.status == 1 else 1
        user.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user.save()
        messages.success(request, 'Status updated successfully')
    except Exception as err:
        print(f"Error updating user status: {str(err)}")
        messages.error(request, 'Failed to update status')
    return redirect('myadmin_user_index', 1)
