from django.urls import path
from . import views

app_name = 'bill'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('zzbill/', views.zzbill, name='zzbill'),
    path('register/', views.register, name='register'),

    # 支出账单管理
    path('zzbill/outcome/list/', views.outcome_list, name='outcome_list'),
    path('zzbill/outcome/list/add', views.outcome_add, name='outcome_add'),
    path('zzbill/outcome/<int:nid>/edit', views.outcome_edit, name='outcome_edit'),
    path('zzbill/outcome/<int:nid>/delete', views.outcome_delete, name='outcome_delete'),

    # 收入账单管理
    path('zzbill/income/list/', views.income_list, name='income_list'),
    path('zzbill/income/list/add', views.income_add, name='income_add'),
    path('zzbill/income/<int:nid>/edit', views.income_edit, name='income_edit'),
    path('zzbill/income/<int:nid>/delete', views.income_delete, name='income_delete'),

    # 数据统计与分析
    path('analysis/', views.analysis, name='analysis'),
    path('analysis/bar/', views.bar, name='bar'),
    path('analysis/pie/', views.pie, name='pie'),
    path('<slug:year_month>/text/', views.text, name='text'),
]