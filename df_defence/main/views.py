import csv
import hashlib
import json
import random
from datetime import datetime, timedelta

import pandas as pd
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Line

from main.DL.cnn.train import main_cnn
from main.DL.cnn_lstm_attention.train import main_attention
from main.DL.lstm import train as lstm_multiclass_train
from main.firewall import FirewallManager
from main.forms import CustomCaptchaForm
from main.models import User, IPAddressRule, TuningModels, TrafficLog
from main.sql.sqlquery import SQLFather
from main.utils import generate_task_id


def login(request):
    captcha_form = CustomCaptchaForm()
    context = {
        "captcha_form": captcha_form,
    }
    return render(request, 'login.html', context)


def do_login(request):
    captcha_form = CustomCaptchaForm()
    try:
        user = User.objects.get(username=request.POST['username'])
        print(user.toDict())
        if user.status == 1:
            import hashlib
            md5 = hashlib.md5()
            s = request.POST['pass'] + user.password_salt
            md5.update(s.encode('utf-8'))
            # 新增验证码
            captcha_form = CustomCaptchaForm(request.POST)
            if captcha_form.is_valid():
                # print(captcha_form.cleaned_data)
                if user.password_hash == md5.hexdigest():
                    request.session['is_login'] = True
                    request.session['login_user'] = user.toDict()

                    # print("用户登录")
                    # print(request.session['login_user'])
                    return redirect('/index')
                else:
                    context = {
                        "captcha_form": captcha_form,
                        "info": '账号或密码错误'
                    }
                    messages.error(request, '账号或密码错误')
                    return render(request, 'login.html', context)
            else:
                context = {
                    "captcha_form": captcha_form,
                    "error": '验证码错误'
                }
                messages.error(request, '验证码错误')
                return render(request, 'login.html', context)
        if user.status == 6:
            import hashlib
            md5 = hashlib.md5()
            s = request.POST['pass'] + user.password_salt
            md5.update(s.encode('utf-8'))
            captcha_form = CustomCaptchaForm(request.POST)
            if captcha_form.is_valid():
                print("验证码正确")
                if user.password_hash == md5.hexdigest():
                    request.session['is_login'] = True
                    request.session['adminuser'] = user.toDict()
                    return redirect(reverse("myadmin_user_index", args=(1,)))
                else:
                    context = {
                        "captcha_form": captcha_form,
                        "info": '密码错误'
                    }
                    messages.error(request, '账号或密码错误')
                    return render(request, 'login.html', context)
        else:
            context = {
                "captcha_form": captcha_form,
                "info": '账号无权限'
            }
            messages.error(request, 'Account has no permission')
    except Exception as e:
        print("Error:", e)
        context = {
            "captcha_form": captcha_form,
            "info": 'Incorrect username or password'
        }
        messages.error(request, 'Incorrect username or password')
    context = {
        "captcha_form": captcha_form,
        "info": 'Incorrect username or password'
    }
    messages.error(request, 'Incorrect username or password')
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)  # 清除当前用户所有session
    print("User session", request.session.get('is_login'))
    return HttpResponseRedirect('login')


def register(request):
    return render(request, 'register.html')


def do_register(request):
    captcha_form = CustomCaptchaForm()
    username = request.POST['username']

    # 检查用户名是否已存在
    if User.objects.filter(username=username).exists():
        # 用户名已存在，返回错误信息或重定向到适当的页面
        error_message = "该用户名已被注册，请选择其他用户名。"
        context = {
            "captcha_form": captcha_form,
            "error": error_message,
        }
        messages.error(request, '该用户名已被注册，请选择其他用户名。')
        return render(request, 'register.html', context)

    import hashlib, random
    md5 = hashlib.md5()
    n = random.randint(100000, 999999)
    s = request.POST['pass'] + str(n)
    md5.update(s.encode('utf-8'))

    ob = User()
    ob.username = username
    ob.password_hash = md5.hexdigest()
    ob.password_salt = n
    ob.status = 1
    ob.create_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ob.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ob.save()

    context = {
        "captcha_form": captcha_form,
    }
    return render(request, 'login.html', context)


def forgot_pd(request):
    captcha_form = CustomCaptchaForm()

    if request.method == 'POST':
        username = request.POST['username']

        try:
            user = User.objects.get(username=username)

            if user.status != 1:
                context = {
                    "captcha_form": captcha_form,
                    "msg": '只有普通用户能够修改密码'
                }
                messages.error(request, '只有普通用户能够修改密码')
                return render(request, 'forgot_pd.html', context)

            captcha_form = CustomCaptchaForm(request.POST)

            if captcha_form.is_valid():
                if not User.objects.filter(username=username).exists():
                    # 用户名不存在，返回错误信息或重定向到适当的页面
                    error_message = "该用户名未注册"
                    context = {
                        "captcha_form": captcha_form,
                        "msg": error_message,
                    }
                    messages.error(request, '该用户名未注册')
                    return render(request, 'forgot_pd.html', context)
                else:
                    # 修改密码
                    md5 = hashlib.md5()
                    n = random.randint(100000, 999999)
                    s = request.POST['pass'] + str(n)
                    md5.update(s.encode('utf-8'))

                    # 更新用户密码信息
                    user.password_hash = md5.hexdigest()
                    user.password_salt = n
                    user.update_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    user.save()

                    context = {
                        "captcha_form": captcha_form,
                        "msg": '密码修改成功'
                    }
                    messages.success(request, 'Password changed successfully')
                    return render(request, 'forgot_pd.html', context)
            else:
                context = {
                    "captcha_form": captcha_form,
                    "msg": 'Incorrect captcha'
                }
                messages.error(request, 'Incorrect captcha')
                return render(request, 'forgot_pd.html', context)

        except User.DoesNotExist:
            # User does not exist, return error message or redirect to appropriate page
            error_message = "This username is not registered"
            context = {
                "captcha_form": captcha_form,
                "msg": error_message,
            }
            messages.error(request, 'This username is not registered')
            return render(request, 'forgot_pd.html', context)

        except Exception as e:
            print(e)
            context = {
                "captcha_form": captcha_form,
                "msg": 'Internal error'
            }
            return render(request, 'forgot_pd.html', context)

    context = {
        "captcha_form": captcha_form,
    }
    return render(request, 'forgot_pd.html', context)


def index(request, *args, **kwargs):
    # 返回页面时，需要判断用户是否已经开始扫描，若开始扫描则应该持续显示该页面
    user_id = request.session['login_user'].get('id')
    user = User.objects.get(id=user_id)

    return render(request, 'index.html')


def screen(request):
    # 获取用户数据
    user_id = request.session['login_user'].get('id')
    user = User.objects.get(id=user_id)

    try:
        # 获取LSTM模型结果
        lstm_model = TuningModels.objects.filter(user=user, tuning_model='LSTM').latest('end_time')
        lstm_metrics = {
            'accuracy': float(lstm_model.accuracy),
            'precision': float(lstm_model.precision1),
            'recall': float(lstm_model.recall),
            'f1': float(lstm_model.f1)
        }

        # 获取CNN模型结果
        cnn_model = TuningModels.objects.filter(user=user, tuning_model='CNN').latest('end_time')
        cnn_metrics = {
            'accuracy': float(lstm_model.accuracy),
            'precision': float(lstm_model.precision1),
            'recall': float(lstm_model.recall),
            'f1': float(lstm_model.f1)
        }

        # 获取CNN-LSTM-ATTENTION模型结果
        cnn_lstm_attention_model = TuningModels.objects.filter(user=user, tuning_model='CNN-LSTM-ATTENTION').latest('end_time')
        cnn_lstm_attention_metrics = {
            'accuracy': float(lstm_model.accuracy),
            'precision': float(lstm_model.precision1),
            'recall': float(lstm_model.recall),
            'f1': float(lstm_model.f1)
        }

    except TuningModels.DoesNotExist:
        lstm_metrics = {'accuracy': 0, 'precision': 0, 'recall': 0, 'f1': 0}
        cnn_metrics = {'accuracy': 0, 'precision': 0, 'recall': 0, 'f1': 0}
        cnn_lstm_attention_metrics = {'accuracy': 0, 'precision': 0, 'recall': 0, 'f1': 0}

    # 生成柱状图
    def generate_bar_chart():
        bar = Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
        
        # 设置X轴数据
        x_axis_data = ['准确率', '精确率', '召回率', 'F1分数']
        bar.add_xaxis(x_axis_data)
        
        # 添加各模型数据
        bar.add_yaxis("LSTM模型", [
            lstm_metrics['accuracy'],
            lstm_metrics['precision'],
            lstm_metrics['recall'],
            lstm_metrics['f1']
        ])
        bar.add_yaxis("CNN模型", [
            cnn_metrics['accuracy'],
            cnn_metrics['precision'],
            cnn_metrics['recall'],
            cnn_metrics['f1']
        ])
        bar.add_yaxis("CNN-LSTM-Attention模型", [
            cnn_lstm_attention_metrics['accuracy'],
            cnn_lstm_attention_metrics['precision'],
            cnn_lstm_attention_metrics['recall'],
            cnn_lstm_attention_metrics['f1']
        ])
        
        # 设置全局配置
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="模型性能指标对比"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            legend_opts=opts.LegendOpts(pos_top="8%"),
            yaxis_opts=opts.AxisOpts(
                name="得分",
                min_=0,
                max_=100,
                interval=20,
                axislabel_opts=opts.LabelOpts(formatter="{value}%")
            )
        )
        
        return bar.render_embed()

    # 生成热力图
    def generate_heatmap():
        from pyecharts.charts import HeatMap
        from pyecharts import options as opts
        
        # 准备数据
        data = [
            [0, 0, lstm_metrics['accuracy']],
            [0, 1, lstm_metrics['precision']],
            [0, 2, lstm_metrics['recall']],
            [0, 3, lstm_metrics['f1']],
            [1, 0, cnn_metrics['accuracy']],
            [1, 1, cnn_metrics['precision']],
            [1, 2, cnn_metrics['recall']],
            [1, 3, cnn_metrics['f1']],
            [2, 0, cnn_lstm_attention_metrics['accuracy']],
            [2, 1, cnn_lstm_attention_metrics['precision']],
            [2, 2, cnn_lstm_attention_metrics['recall']],
            [2, 3, cnn_lstm_attention_metrics['f1']]
        ]
        
        heatmap = HeatMap(init_opts=opts.InitOpts(width="100%", height="400px"))
        heatmap.add_xaxis(['LSTM', 'CNN', 'CNN-LSTM-Attention'])
        heatmap.add_yaxis(
            "性能指标",
            ['准确率', '精确率', '召回率', 'F1分数'],
            data,
            label_opts=opts.LabelOpts(is_show=True, position="inside")
        )
        
        heatmap.set_global_opts(
            title_opts=opts.TitleOpts(title="模型性能热力图"),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=100,
                is_calculable=True,
                orient="horizontal",
                pos_left="center",
                pos_bottom="5%"
            )
        )
        
        return heatmap.render_embed()

    data = {
        'status': 'success',
        'bar_chart': generate_bar_chart(),
        'heatmap': generate_heatmap()
    }

    return render(request, 'screen.html', data)


def dataset_result(request):
    import os
    main_dir = 'main/DL/data'
    model_path = os.path.join(main_dir, f'cic2017_train.csv')
    df = pd.read_csv(model_path)

    df['attack_category'] = df[' Label']
    print(f"攻击类型分布为：{df['attack_category']}")

    # 1. 攻击类型分布饼图
    attack_dist = (
        Pie(init_opts=opts.InitOpts(width="100%", height="400px"))
        .add(
            "",
            [list(z) for z in df['attack_category'].value_counts().items()],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="攻击类型分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
        )
    )

    # 2. Total Fwd Packets top10 总前向数据包
    x_values = list(range(1, 11))
    top10_packet = df[' Total Fwd Packets'].nlargest(10)

    protocol_stats = (
        Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
        .add_xaxis(x_values)
        .add_yaxis("总前向数据包", top10_packet.values.round(2).tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="总前向数据包"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            toolbox_opts=opts.ToolboxOpts()
        )
    )

    # 3.数据包的平均大小
    top10_flow = df[' Average Packet Size'].nlargest(10)  # 取前10个最大值
    x_values = list(range(1, 11))
    service_top10 = (
        Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
        .add_xaxis(x_values)  # X轴：从 1 到 10
        .add_yaxis("数据包的平均大小", top10_flow.values.round(2).tolist())  # Y轴：流量数值，保留两位小数
        .set_global_opts(
            title_opts=opts.TitleOpts(title="数据包的平均大小TOP10"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            toolbox_opts=opts.ToolboxOpts()
        )
    )

    # 4. 连接时长分布折线图
    duration_stats = (
        Line(init_opts=opts.InitOpts(width="100%", height="400px"))
        .add_xaxis(
            [str(x) for x in range(10)]
        )
        .add_yaxis(
            "连接数量",
            df[' Flow Duration'].value_counts().sort_index().head(10).values.tolist(),
            is_smooth=True
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="连接时长分布(前10个时间点)"),
            toolbox_opts=opts.ToolboxOpts()
        )
    )

    data = {
        'status': 'success',
        'attack_dist': attack_dist.dump_options(),
        'protocol_stats': protocol_stats.dump_options(),
        'service_top10': service_top10.dump_options(),
        'duration_stats': duration_stats.dump_options(),
    }

    return render(request, 'dataset_result.html', data)


def model_tuning(request):
    data = {
        'status': 'success',
    }
    return render(request, 'model_tuning.html', data)



def tuning_lstm(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lr = float(data.get('lr', 5e-6))
            wd = float(data.get('wd', 6e-6))
            batch_size = int(data.get('batch_size', 256))
            num_epochs = int(data.get('num_epochs', 20))
            accuracy, loss, test_accuracy = lstm_multiclass_train.main(
                num_epochs=num_epochs,
                lr=lr,
                wd=wd,
                batch_size=batch_size
            )

            user_id = request.session['login_user'].get('id')
            user = User.objects.get(id=user_id)
            tuning_task = TuningModels.objects.create(
                tuning_id=generate_task_id(),
                user=user,
                tuning_model='LSTM',
                start_time=timezone.now(),
                end_time=timezone.now(),
                lr=lr,
                wd=wd,
                batch_size=batch_size,
                num_epochs=num_epochs,
                accuracy=f"{accuracy * 100:.2f}",
                loss=f"{loss:.2f}",
                test_accuracy=f"{test_accuracy:.2f}"
            )
            tuning_task.save()

            return JsonResponse({
                'status': 'success',
                'accuracy': f"{accuracy * 100:.2f}",
                'loss': f"{loss:.2f}",
                'test_accuracy': f"{test_accuracy:.2f}",
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)


def reset_parameter_lstm(request):
    # 重置参数为默认值
    default_params = {
        'lr': 5e-4,
        'wd': 1e-5,
        'batch_size': 256,
        'num_epochs': 1,
    }
    return render(request, 'do_tuning_lstm_multi.html', context=default_params)


def ip_rule_list(request):
    """显示IP规则列表"""
    whitelist = IPAddressRule.objects.filter(rule_type='white')
    blacklist = IPAddressRule.objects.filter(rule_type='black')

    context = {
        'whitelist': whitelist,
        'blacklist': blacklist
    }
    return render(request, 'myadmin/ip_rules.html', context)


def add_ip_rule(request):
    """添加IP规则"""
    if request.method == 'POST':
        ip_address = request.POST.get('ip_address')
        rule_type = request.POST.get('rule_type')
        description = request.POST.get('description', '')

        try:
            # 检查IP是否已存在
            if IPAddressRule.objects.filter(ip_address=ip_address).exists():
                messages.error(request, f'IP地址 {ip_address} 已存在于规则列表中')
                return redirect('ip_rule_list')

            # 添加防火墙规则
            if FirewallManager.add_rule(ip_address, rule_type):
                # 保存到数据库
                IPAddressRule.objects.create(
                    ip_address=ip_address,
                    rule_type=rule_type,
                    description=description
                )
                messages.success(request, f'成功添加{rule_type}规则：{ip_address}')
            else:
                messages.error(request, f'添加防火墙规则失败：{ip_address}')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'添加规则时发生错误：{str(e)}')

    return redirect('ip_rule_list')


def delete_ip_rule(request, rule_id):
    """删除IP规则"""
    try:
        rule = IPAddressRule.objects.get(id=rule_id)

        # 删除防火墙规则
        if FirewallManager.remove_rule(rule.ip_address, rule.rule_type):
            # 从数据库中删除
            rule.delete()
            messages.success(request, f'成功删除规则：{rule.ip_address}')
        else:
            messages.error(request, f'删除防火墙规则失败：{rule.ip_address}')

    except IPAddressRule.DoesNotExist:
        messages.error(request, '规则不存在')
    except Exception as e:
        messages.error(request, f'删除规则时发生错误：{str(e)}')

    return redirect('ip_rule_list')



def tuning_lstm_duofenlei(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lr = float(data.get('lr', 8e-5))
            wd = float(data.get('wd', 6e-6))
            batch_size = int(data.get('batch_size', 256))
            num_epochs = int(data.get('num_epochs', 20))

            test_accuracy, test_precision, test_recall, test_f1 = lstm_multiclass_train.main(
                num_epochs=num_epochs,
                lr=lr,
                wd=wd,
                batch_size=batch_size,
            )

            user_id = request.session['login_user'].get('id')
            user = User.objects.get(id=user_id)
            tuning_task = TuningModels.objects.create(
                tuning_id=generate_task_id(),
                user=user,
                tuning_model='LSTM',
                start_time=timezone.now(),
                end_time=timezone.now(),
                lr=lr,
                wd=wd,
                batch_size=batch_size,
                num_epochs=num_epochs,
                accuracy=f"{test_accuracy * 100:.2f}",
                precision1=f"{test_precision * 100:.2f}",
                recall=f"{test_recall * 100:.2f}",
                f1=f"{test_f1 * 100:.2f}",
            )
            tuning_task.save()

            return JsonResponse({
                'status': 'success',
                'accuracy': f"{test_accuracy * 100:.2f}",
                'precision1': f"{test_precision * 100:.2f}",
                'recall': f"{test_recall * 100:.2f}",
                'f1': f"{test_f1 * 100:.2f}"
            })
            # return JsonResponse({
            #     'status': 'success',
            #     'accuracy': f"{0.1 * 100:.2f}",
            #     'precision1': f"{0.1 * 100:.2f}",
            #     'recall': f"{0.1 * 100:.2f}",
            #     'f1': f"{0.1 * 100:.2f}"
            # })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)


def tuning_cnn_duofenlei(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lr = float(data.get('lr', 8e-5))
            wd = float(data.get('wd', 6e-6))
            batch_size = int(data.get('batch_size', 256))
            num_epochs = int(data.get('num_epochs', 20))

            test_accuracy, test_precision, test_recall, test_f1 = main_cnn(
                num_epochs=num_epochs,
                lr=lr,
                wd=wd,
                batch_size=batch_size,
            )

            user_id = request.session['login_user'].get('id')
            user = User.objects.get(id=user_id)
            tuning_task = TuningModels.objects.create(
                tuning_id=generate_task_id(),
                user=user,
                tuning_model='CNN',
                start_time=timezone.now(),
                end_time=timezone.now(),
                lr=lr,
                wd=wd,
                batch_size=batch_size,
                num_epochs=num_epochs,
                accuracy=f"{test_accuracy * 100:.2f}",
                precision1=f"{test_precision * 100:.2f}",
                recall=f"{test_recall * 100:.2f}",
                f1=f"{test_f1 * 100:.2f}",
            )
            tuning_task.save()

            return JsonResponse({
                'status': 'success',
                'accuracy': f"{test_accuracy * 100:.2f}",
                'precision1': f"{test_precision * 100:.2f}",
                'recall': f"{test_recall * 100:.2f}",
                'f1': f"{test_f1 * 100:.2f}"
            })
            # return JsonResponse({
            #     'status': 'success',
            #     'accuracy': f"{0.1 * 100:.2f}",
            #     'precision1': f"{0.1 * 100:.2f}",
            #     'recall': f"{0.1 * 100:.2f}",
            #     'f1': f"{0.1 * 100:.2f}"
            # })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)

def tuning_cnn_lstm_att_duofenlei(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lr = float(data.get('lr', 8e-5))
            wd = float(data.get('wd', 6e-6))
            batch_size = int(data.get('batch_size', 256))
            num_epochs = int(data.get('num_epochs', 20))

            test_accuracy, test_precision, test_recall, test_f1 = main_attention(
                num_epochs=num_epochs,
                lr=lr,
                wd=wd,
                batch_size=batch_size,
            )

            user_id = request.session['login_user'].get('id')
            user = User.objects.get(id=user_id)
            tuning_task = TuningModels.objects.create(
                tuning_id=generate_task_id(),
                user=user,
                tuning_model='CNN-LSTM-ATTENTION',
                start_time=timezone.now(),
                end_time=timezone.now(),
                lr=lr,
                wd=wd,
                batch_size=batch_size,
                num_epochs=num_epochs,
                accuracy=f"{test_accuracy* 100:.2f}",
                precision1=f"{test_precision * 100:.2f}",
                recall=f"{test_recall * 100:.2f}",
                f1=f"{test_f1 * 100:.2f}",
            )
            tuning_task.save()

            return JsonResponse({
                'status': 'success',
                'accuracy': f"{test_accuracy * 100:.2f}",
                'precision1': f"{test_precision * 100:.2f}",
                'recall': f"{test_recall * 100:.2f}",
                'f1': f"{test_f1 * 100:.2f}"
            })
            # return JsonResponse({
            #     'status': 'success',
            #     'accuracy': f"{0.1 * 100:.2f}",
            #     'precision1': f"{0.1 * 100:.2f}",
            #     'recall': f"{0.1 * 100:.2f}",
            #     'f1': f"{0.1 * 100:.2f}"
            # })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)

def do_tuning_lstm_multi(request):
    user_id = request.session['login_user'].get('id')
    user = User.objects.get(id=user_id)
    # 查询最新的调优任务记录
    latest_tuning_task = TuningModels.objects.filter(user=user, tuning_model='LSTM').order_by('-created_at').first()
    if latest_tuning_task:
        context = {
            'lr': latest_tuning_task.lr,
            'wd': latest_tuning_task.wd,
            'batch_size': latest_tuning_task.batch_size,
            'num_epochs': latest_tuning_task.num_epochs,
            'accuracy': latest_tuning_task.accuracy,
            'precision1': latest_tuning_task.precision1,
            'recall': latest_tuning_task.recall,
            'f1': latest_tuning_task.f1,
        }
    else:
        context = {}
    return render(request, 'do_tuning_lstm_multi.html', context)

def get_dashboard_stats(request):
    """获取仪表盘统计数据"""
    try:
        # 获取今日告警总数
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        # 使用SQL查询获取统计数据
        sql_query = SQLFather()

        # 获取告警统计
        stats = sql_query.getAlertStats(
            start_time=today,
            end_time=tomorrow
        )

        # 获取告警趋势数据
        trend_data = sql_query.getAlertTrend(
            start_time=today
        )

        # 获取告警类型分布
        alert_types = sql_query.getAlertTypes(
            start_time=today,
            end_time=tomorrow
        )

        # 获取最近告警日志
        _, recent_alerts = sql_query.getTrafficLogs(
            start_time=today,
            end_time=tomorrow,
            page_size=10
        )

        return JsonResponse({
            'status': 'success',
            'data': {
                'stats': {
                    'total_alerts': stats['total'],
                    'high_alerts': stats['high'],
                    'medium_alerts': stats['medium'],
                    'low_alerts': stats['low']
                },
                'trend_data': trend_data,
                'alert_types': alert_types,
                'recent_alerts': recent_alerts
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# 流量日志相关视图函数
def traffic_log_list(request):
    """显示流量日志列表"""
    try:
        # 获取查询参数
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        src_ip = request.GET.get('src_ip')
        dst_ip = request.GET.get('dst_ip')
        protocol = request.GET.get('protocol')
        attack_type = request.GET.get('attack_type')
        threat = request.GET.get('threat')

        # 构建查询条件
        query = {}
        if start_time:
            query['create_time__gte'] = start_time
        if end_time:
            query['create_time__lte'] = end_time
        if src_ip:
            query['src_ip__icontains'] = src_ip
        if dst_ip:
            query['dst_ip__icontains'] = dst_ip
        if protocol:
            query['protocol'] = protocol
        if attack_type:
            query['attack_type'] = attack_type
        if threat:
            query['threat'] = threat

        # 获取日志列表
        traffic_logs = TrafficLog.objects.filter(**query).order_by('-create_time')

        # 分页
        paginator = Paginator(traffic_logs, 10)
        page = request.GET.get('page')
        try:
            traffic_logs = paginator.page(page)
        except PageNotAnInteger:
            traffic_logs = paginator.page(1)
        except EmptyPage:
            traffic_logs = paginator.page(paginator.num_pages)

        return render(request, 'traffic_log.html', {
            'traffic_logs': traffic_logs
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def traffic_log_detail(request, log_id):
    """获取流量日志详情"""
    try:
        log = TrafficLog.objects.get(id=log_id)
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': log.id,
                'create_time': log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'src_ip': log.src_ip,
                'dst_ip': log.dst_ip,
                'src_port': log.src_port,
                'dst_port': log.dst_port,
                'protocol': log.protocol,
                'features': log.features,
                'attack_type': log.attack_type,
                'threat': log.threat
            }
        })
    except TrafficLog.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '日志不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def traffic_log_detete(request, log_id):
    """删除单个流量日志"""
    try:
        TrafficLog.objects.get(id=log_id).delete()
        return JsonResponse({
            'status': 'success',
            'message': '删除成功'
        })
    except TrafficLog.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '日志不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def traffic_log_batch_delete(request):
    """批量删除流量日志"""
    if request.method == 'POST':
        try:
            ids = request.POST.getlist('ids[]')
            TrafficLog.objects.filter(id__in=ids).delete()
            return JsonResponse({
                'status': 'success',
                'message': '删除成功'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': '仅支持POST请求'
    }, status=405)


def traffic_log_export(request):
    """导出流量日志为CSV"""
    try:
        # 获取查询参数
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        src_ip = request.GET.get('src_ip')
        dst_ip = request.GET.get('dst_ip')
        protocol = request.GET.get('protocol')
        attack_type = request.GET.get('attack_type')
        threat = request.GET.get('threat')

        # 构建查询条件
        query = {}
        if start_time:
            query['create_time__gte'] = start_time
        if end_time:
            query['create_time__lte'] = end_time
        if src_ip:
            query['src_ip__icontains'] = src_ip
        if dst_ip:
            query['dst_ip__icontains'] = dst_ip
        if protocol:
            query['protocol'] = protocol
        if attack_type:
            query['attack_type'] = attack_type
        if threat:
            query['threat'] = threat

        # 获取日志数据
        logs = TrafficLog.objects.filter(**query).order_by('-create_time')

        # 创建CSV响应
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="traffic_logs.csv"'

        # 写入CSV数据
        writer = csv.writer(response)
        writer.writerow([
            '创建时间', '源IP地址', '目标IP地址', '源端口', '目标端口',
            '协议', '特征内容', '攻击类型', '威胁级别'
        ])

        for log in logs:
            writer.writerow([
                log.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                log.src_ip,
                log.dst_ip,
                log.src_port,
                log.dst_port,
                log.protocol,
                log.features,
                log.attack_type or '正常',
                log.threat or '正常'
            ])

        return response
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def do_tuning_cnn(request):
    user_id = request.session['login_user'].get('id')
    user = User.objects.get(id=user_id)
    # 查询最新的调优任务记录
    latest_tuning_task = TuningModels.objects.filter(user=user, tuning_model='CNN').order_by('-created_at').first()
    if latest_tuning_task:
        context = {
            'lr': latest_tuning_task.lr,
            'wd': latest_tuning_task.wd,
            'batch_size': latest_tuning_task.batch_size,
            'num_epochs': latest_tuning_task.num_epochs,
            'accuracy': latest_tuning_task.accuracy,
            'precision1': latest_tuning_task.precision1,
            'recall': latest_tuning_task.recall,
            'f1': latest_tuning_task.f1,
        }
    else:
        context = {}
    return render(request, 'do_tuning_cnn.html', context)

def do_tuning_cnn_lstm_attention(request):
    user_id = request.session['login_user'].get('id')
    user = User.objects.get(id=user_id)
    # 查询最新的调优任务记录
    latest_tuning_task = TuningModels.objects.filter(user=user, tuning_model='CNN-LSTM-ATTENTION').order_by('-created_at').first()
    if latest_tuning_task:
        context = {
            'lr': latest_tuning_task.lr,
            'wd': latest_tuning_task.wd,
            'batch_size': latest_tuning_task.batch_size,
            'num_epochs': latest_tuning_task.num_epochs,
            'accuracy': latest_tuning_task.accuracy,
            'precision1': latest_tuning_task.precision1,
            'recall': latest_tuning_task.recall,
            'f1': latest_tuning_task.f1,
        }
    else:
        context = {}
    return render(request, 'do_tuning_cnn_lstm_attention.html', context)
