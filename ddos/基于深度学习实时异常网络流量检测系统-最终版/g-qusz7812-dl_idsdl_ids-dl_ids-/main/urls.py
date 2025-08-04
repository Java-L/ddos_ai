from django.urls import path
from . import user

from main import views

urlpatterns = [
    # 基础服务
    path('', views.login, name="myadmin_login"),
    path('login', views.login, name="myadmin_login2"),
    path('dologin', views.do_login, name="myadmin_do_login"),
    path('logout', views.logout_view, name="myadmin_logout"),
    path('register', views.register, name="myadmin_register"),
    path('doregister', views.do_register, name="myadmin_do_register"),
    path('forgot_pd', views.forgot_pd, name="forgot_pd"),
    # 管理员
    path('user/<int:pIndex>', user.index, name="myadmin_user_index"),
    path('user/insert', user.insert, name="myadmin_user_insert"),
    path('user/delete/<int:uid>', user.delete, name="myadmin_user_delete"),
    path('user/edit/<int:uid>', user.edit, name="myadmin_user_edit"),
    path('user/update/<int:uid>', user.update, name="myadmin_user_update"),

    # 模型展示
    path('index', views.index, name="ids_index"),
    path('screen', views.screen, name="ids_screen"),

    # 模型测试集
    path('dataset_res', views.dataset_result, name="ids_dataset_result"),

    # 模型调优
    path('model_tuning', views.model_tuning, name="ids_model_tuning"),
    path('do_tuning_lstm', views.do_tuning_lstm_multi, name="do_tuning_lstm"),
    path('do_tuning_cnn', views.do_tuning_cnn, name="do_tuning_cnn"),
    path('do_tuning_cnn_lstm_attention', views.do_tuning_cnn_lstm_attention, name="do_tuning_cnn_lstm_attention"),

    path('tuning_lstm_duofenlei/', views.tuning_lstm_duofenlei, name='tuning_lstm_duofenlei'),
    path('tuning_cnn_duofenlei/', views.tuning_cnn_duofenlei, name='tuning_cnn_duofenlei'),
    path('tuning_cnn_lstm_att_duofenlei/', views.tuning_cnn_lstm_att_duofenlei, name='tuning_cnn_lstm_att_duofenlei'),
    path('reset_parameter_lstm/', views.reset_parameter_lstm, name='reset_parameter_lstm'),

    # IP规则管理
    path('ip-rules/', views.ip_rule_list, name='ip_rule_list'),
    path('ip-rules/add/', views.add_ip_rule, name='add_ip_rule'),
    path('ip-rules/delete/<int:rule_id>/', views.delete_ip_rule, name='delete_ip_rule'),

    # 仪表盘数据接口
    path('api/dashboard/stats', views.get_dashboard_stats, name='dashboard_stats'),

    # 流量日志相关接口
    path('traffic-log/', views.traffic_log_list, name='ids_traffic_log'),
    path('api/traffic-log/<int:log_id>/', views.traffic_log_detail, name='traffic_log_detail'),
    path('api/traffic-log-delete/<int:log_id>/', views.traffic_log_detete, name='traffic_log_detete'),
    path('api/traffic-log/batch-delete/', views.traffic_log_batch_delete, name='traffic_log_batch_delete'),
    path('api/traffic-log/export/', views.traffic_log_export, name='traffic_log_export'),
]
