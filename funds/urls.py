from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'funds'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('fund_info/<str:code_id>/', views.fund_info, name='fund_info'),
]
