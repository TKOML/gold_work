# myfunds/urls.py
from django.urls import path
from . import views

app_name = 'myfunds'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('fund-list/', views.send_fund_list, name="fund-list"),
    path('add-holding/', views.add_holding, name="add-holding"),  # 确保路径末尾有 '/'
    path('update-prices/', views.update_values, name="update-prices"),
]
