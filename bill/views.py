import datetime
import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from django.contrib import messages  # 确保这一行存在
from django import forms
from django.core.exceptions import ValidationError
from bill import models
from bill.utils.page import Pagination
from django.http import JsonResponse

from .models import UserImformation

def virtual_world(request):
    return render(request, 'virtual_world.html')


import os
import json
from django.http import JsonResponse
from django.shortcuts import render
from openai import OpenAI  # 假设您使用的是OpenAI库来与通义千问API交互
from django.core.cache import cache  # 使用Django缓存来保存对话上下文


def ai_chat(request):
    info_dict = request.session.get("info", {})
    name = info_dict.get('name', '游客')

    system_message = (
        "你是一位专业的记账小助手，专注于帮助用户管理和优化个人财务管理。"
        "你的任务包括但不限于解答有关记账、预算编制、储蓄计划、投资理财等方面的问题。"
        "你应该用清晰易懂的语言解释复杂的金融术语，并根据用户的实际情况给出个性化的建议。"
        "始终保持友好、耐心的态度，尊重用户隐私，只在用户明确询问时才提供具体的投资产品推荐。"
    )

    user_id = request.session.session_key or ''  # 获取当前用户的唯一标识符

    if request.method == 'POST':
        try:
            message = request.POST.get('message', '').strip()
            if not message:
                return JsonResponse({
                    'success': False,
                    'error': '请输入有效的消息内容'
                })

            # 获取并更新对话上下文
            conversation_history = cache.get(user_id, [])
            conversation_history.append({'role': 'user', 'content': message})

            # 添加系统消息到对话历史中
            if len(conversation_history) == 1:  # 只在第一次对话时添加系统消息
                conversation_history.insert(0, {'role': 'system', 'content': system_message})

            client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=conversation_history
            )

            response_content = completion.choices[0].message.content.strip()
            conversation_history.append({'role': 'assistant', 'content': response_content})

            # 更新缓存中的对话历史
            cache.set(user_id, conversation_history, timeout=None)

            return JsonResponse({
                'success': True,
                'response': response_content
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f"请求失败: {str(e)}"
            })

    # 渲染页面时，清除对话历史以确保每次打开聊天都是新的会话
    cache.delete(user_id)

    return render(request, 'ai_chat.html', {"name": name})


# 可选：添加一个视图用于清除特定用户的对话历史
def clear_conversation(request):
    user_id = request.session.session_key or ''
    cache.delete(user_id)
    return JsonResponse({
        'success': True,
        'message': '对话历史已清除'
    })
class UserModelForm(forms.ModelForm):
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.UserImformation
        fields = ["name", "password", "confirm_password", "phone", "age", "gender"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("密码不一致!")
        return confirm_password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


class OutcomeModelForm(forms.ModelForm):
    class Meta:
        model = models.BillOutcome
        fields = ["time_out", "account_type_out", "classify_type_out", "money_out", "notes_out"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


class IncomeModelForm(forms.ModelForm):
    class Meta:
        model = models.BillIncome
        fields = ["time_in", "account_type_in", "classify_type_in", "money_in", "notes_in"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


class LoginForm(forms.Form):
    user_name = forms.CharField(label="用户名",widget=forms.TextInput,required=True)
    user_password = forms.CharField(label="密码",widget=forms.PasswordInput,required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    # user_name = request.POST.get("user")
    # user_password = request.POST.get("password")
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user_object = models.UserImformation.objects.filter(name=form.cleaned_data.get("user_name"), password=form.cleaned_data.get("user_password")).first()
        if not user_object:
            form.add_error("user_password", "用户名或者密码错误!")
            return render(request, 'login.html', {"form": form})

        request.session["info"] = {'name': user_object.name}
        request.session.set_expiry(60*60)

        return redirect("bill:index")
        # error = "用户名或者密码错误!"
        # return render(request, 'login.html', {"error": error})

    return render(request, 'login.html', {"form": form})


def zzbill(request):
    info_dict = request.session.get("info")
    name = info_dict.get('name')
    return render(request, 'zzbill.html', {"name": name})


def register(request):
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'register.html', {"form": form})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('bill:login')

    return render(request, 'register.html', {'form': form})


def outcome_list(request):
    data_dict = {}
    search_data = request.GET.get('time', "")
    if search_data:
        year = search_data[0:4]
        month = search_data[5:7]
        if month[0] == '0':
            month = month[1]

        info_dict = request.session.get("info")
        name = info_dict.get('name')
        queryset1 = models.BillOutcome.objects.filter(belong_out=name).order_by("time_out")
        queryset = []
        for result in queryset1:
            if (str(result.time_out.year) == year) & (str(result.time_out.month) == month):
                queryset.append(result)
        page_object = Pagination(request, queryset)
        context_dict = {
            "name": name,
            "search_data": search_data,
            # "queryset": queryset,
            "queryset": page_object.page_queryset,
            "page_string": page_object.html()
        }
        return render(request, 'outcome_list.html', context_dict)

    info_dict = request.session.get("info")
    name = info_dict.get('name')
    queryset1 = models.BillOutcome.objects.filter(belong_out=name).order_by("time_out")
    page_object = Pagination(request, queryset1)
    context_dict = {
        "name": name,
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }
    return render(request, 'outcome_list.html', context_dict)


def outcome_add(request):
    if request.method == "GET":
        form = OutcomeModelForm()
        return render(request, 'outcome_add.html', {"form": form})
    form = OutcomeModelForm(data=request.POST)
    # print(form.cleaned_data)
    if form.is_valid():
        info_dict = request.session.get("info")
        name = info_dict.get('name')
        form.instance.belong_out = name  # instance方法添加额外数据.字段名 = 数据
        form.save()
        return redirect('bill:outcome_list')
    return render(request, 'outcome_add.html', {"form": form})


def outcome_edit(request, nid):
    row = models.BillOutcome.objects.filter(id=nid).first()
    if request.method == "GET":
        form = OutcomeModelForm(instance=row)
        return render(request, 'outcome_edit.html', {"form": form})
    form = OutcomeModelForm(data=request.POST, instance=row)
    if form.is_valid():
        form.save()
        return redirect('bill:outcome_list')
    return render(request, 'outcome_edit.html')


def outcome_delete(request, nid):
    models.BillOutcome.objects.filter(id=nid).delete()
    return redirect('bill:outcome_list')


def income_list(request):
    search_data = request.GET.get('time', "")
    if search_data:
        year = search_data[0:4]
        month = search_data[5:7]
        if month[0] == '0':
            month = month[1]
        info_dict = request.session.get("info")
        name = info_dict.get('name')
        queryset1 = models.BillIncome.objects.filter(belong_in=name).order_by("time_in")
        queryset = []
        for result in queryset1:
            if (str(result.time_in.year) == year) & (str(result.time_in.month) == month):
                queryset.append(result)
        page_object = Pagination(request, queryset)
        context_dict = {
            "name": name,
            "search_data": search_data,
            "queryset": page_object.page_queryset,
            "page_string": page_object.html()
        }
        return render(request, 'income_list.html', context_dict)
    info_dict = request.session.get("info")
    name = info_dict.get('name')
    queryset1 = models.BillIncome.objects.filter(belong_in=name).order_by("time_in")
    page_object = Pagination(request, queryset1)
    context_dict = {
        "name": name,
        "search_data": search_data,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }
    return render(request, 'income_list.html', context_dict)


def income_add(request):
    if request.method == "GET":
        form = IncomeModelForm()
        return render(request, 'income_add.html', {"form": form})
    form = IncomeModelForm(data=request.POST)
    # print(form.cleaned_data)
    if form.is_valid():
        info_dict = request.session.get("info")
        name = info_dict.get('name')
        form.instance.belong_in = name  # instance方法添加额外数据.字段名 = 数据
        form.save()
        return redirect('bill:income_list')
    return render(request, 'income_add.html', {"form": form})


def income_edit(request, nid):
    row = models.BillIncome.objects.filter(id=nid).first()
    if request.method == "GET":
        form = IncomeModelForm(instance=row)
        return render(request, 'income_edit.html', {"form": form})
    form = IncomeModelForm(data=request.POST, instance=row)
    if form.is_valid():
        form.save()
        return redirect('bill:income_list')
    return render(request, 'income_edit.html')


def income_delete(request, nid):
    models.BillIncome.objects.filter(id=nid).delete()
    return redirect('bill:income_list')


def index(request):
    # 假设你有一个用户的名字或者其他动态信息
    context = {
        'name': '用户',
    }
    return render(request, 'index.html', context)

def profile(request):
    try:
        # 获取当前登录用户的详细信息
        user_info = UserImformation.objects.get(name=request.session["info"]["name"])
    except UserImformation.DoesNotExist:
        # 如果没有找到用户信息，重定向到登录页面或给出提示
        return redirect('bill:login')

    context = {
        'user_info': user_info,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'profile.html', context)

def update_profile(request):
    try:
        user_info = get_object_or_404(UserImformation, name=request.session["info"]["name"])
    except KeyError:
        return redirect('bill:login')

    if request.method == 'POST':
        form = UserModelForm(request.POST, instance=user_info)
        if form.is_valid():
            form.save()
            messages.success(request, '您的个人信息已成功更新！')
            return redirect('bill:profile')
        else:
            messages.error(request, '请检查输入的信息是否正确。')
            return render(request, 'profile.html', {'form': form, 'user_info': user_info})
    else:
        form = UserModelForm(instance=user_info)

    return render(request, 'profile.html', {'form': form, 'user_info': user_info})


def analysis(request):
    search_data = request.GET.get("year_month")
    if search_data:
        year = search_data[0:4]
        month = search_data[5:7]
        if month[0] == '0':
            month = month[1]
        if month == '2':
            day_num = 29
        elif (month == '4')|(month == '6')|(month == '9')|(month == '11'):
            day_num = 30
        else:
            day_num = 31
        x = []                     # x轴参数
        for i in range(day_num):
            x.append(str(i+1)+"日")
        legend = ["支出", "收入"]
        info_dict = request.session.get("info")
        name = info_dict.get('name')
        queryset_in = models.BillIncome.objects.filter(belong_in=name).order_by("time_in")
        queryset_out = models.BillOutcome.objects.filter(belong_out=name).order_by("time_out")
        m_in = []
        m_out = []
        t_out = []
        t_in = []
        income = 0
        outcome = 0
        for j in range(day_num):
            m_in.append(0)
            m_out.append(0)
        for k in range(9):
            t_out.append(0)
        for m in range(10):
            t_in.append(0)
        for r_1 in queryset_in:
            if (str(r_1.time_in.year) == year) & (str(r_1.time_in.month) == month):
                m_in[r_1.time_in.day] = m_in[r_1.time_in.day] + float(r_1.money_in)
                t_in[int(r_1.classify_type_in)-1] += float(r_1.money_in)
                income += float(r_1.money_in)
        for r_2 in queryset_out:
            if (str(r_2.time_out.year) == year) & (str(r_2.time_out.month) == month):
                m_out[r_2.time_out.day] = m_out[r_2.time_out.day] + float(r_2.money_out)
                t_out[int(r_2.classify_type_out)-1] += float(r_2.money_out)
                outcome += float(r_2.money_out)
        surplus = income - outcome
        series_list = [
            {
                "name": '支出',
                "type": 'bar',
                "data": m_out
            },
            {
                "name": '收入',
                "type": 'bar',
                "data": m_in
            }
        ]
        data_list = [
            {"value": t_out[0], "name": '餐饮'},
            {"value": t_out[1], "name": '交通'},
            {"value": t_out[2], "name": '购物'},
            {"value": t_out[3], "name": '居家'},
            {"value": t_out[4], "name": '娱乐'},
            {"value": t_out[5], "name": '人情'},
            {"value": t_out[6], "name": '医疗'},
            {"value": t_out[7], "name": '金融'},
            {"value": t_out[8], "name": '其他'},
        ]
        data_list_2 = [
            {"value": t_in[0], "name": '工资'},
            {"value": t_in[1], "name": '兼职'},
            {"value": t_in[2], "name": '经营'},
            {"value": t_in[3], "name": '利息'},
            {"value": t_in[4], "name": '奖金'},
            {"value": t_in[5], "name": '加班'},
            {"value": t_in[6], "name": '基金'},
            {"value": t_in[7], "name": '股票'},
            {"value": t_in[8], "name": '债券'},
            {"value": t_in[9], "name": '其他'},
        ]

        context_dict = {
            "name": name,
            "search_data": search_data,
            'legend': legend,
            'series_list': series_list,
            'x_axis': x,
            "data": data_list,
            "data_2": data_list_2,
            "income": income,
            "outcome": outcome,
            "surplus": surplus,
        }
        print(context_dict)
        return render(request, 'analysis.html', context_dict)
    else:
        info_dict = request.session.get("info")
        name = info_dict.get('name')
        context_dict = {
            "name": name,
            "search_data": search_data,
        }
        return render(request, 'analysis.html', context_dict)


def bar(request):
    legend = ["梁吉宁", "武沛齐"]
    series_list = [
        {
            "name": '梁吉宁',
            "type": 'bar',
            "data": [15, 20, 36, 10, 10, 10]
        },
        {
            "name": '武沛齐',
            "type": 'bar',
            "data": [45, 10, 66, 40, 20, 50]
        }
    ]
    x_axis = ['1月', '2月', '4月', '5月', '6月', '7月']

    result = {
        "status": True,
        "data": {
            'legend': legend,
            'series_list': series_list,
            'x_axis': x_axis,
        }
    }
    return JsonResponse(result)


def pie(request):
    db_data_list = [
        {"value": 2048, "name": 'IT部门'},
        {"value": 1735, "name": '运营'},
        {"value": 580, "name": '新媒体'},
    ]

    result = {
        "status": True,
        "data": db_data_list
    }
    return JsonResponse(result)


def text(request, a=" "):
    return render(request, 'text.html')
# def delete_profile(request):
#     # 检查是否存在 session 信息
#     if not request.session.get("info"):
#         messages.error(request, "未登录或会话已过期，请重新登录。")
#         return redirect('bill:login')
#
#     try:
#         # 检查用户是否存在
#         user_info = UserImformation.objects.filter(name=request.session["info"]["name"]).first()
#         if not user_info:
#             messages.error(request, "未找到对应的用户信息。")
#             return redirect('bill:profile')
#
#         # 删除用户信息
#         if request.method == "POST":
#             user_info.delete()
#             request.session.flush()  # 清除 session
#             messages.success(request, "您的账户已成功注销。")
#             return redirect('bill:index')
#     except Exception as e:
#         messages.error(request, f"发生错误：{str(e)}")
#         return redirect('bill:profile')
#
#     return redirect('bill:profile')

def money(request):
    return render(request, 'money.html')
def status(request):
    return render(request, 'status.html')
def day_goal(request):
    return render(request, 'day_goal.html')
# bill/views.py


def redirect_to_funds_index(request):
    return redirect('funds:index')




from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password
def redirect_to_funds_index(request):
    return redirect('funds:index')


#最后的
@login_required
def profile_view(request):
    """个人中心页面视图"""
    user_info = UserImformation.objects.get(user=request.user)
    context = {
        'user_info': user_info
    }
    return render(request, 'profile.html', context)


@login_required
@require_http_methods(["POST"])
@login_required
@require_http_methods(["POST"])
def profile_update(request):
    """更新个人信息"""
    try:
        user_info = UserImformation.objects.get(user=request.user)

        user_info.name = request.POST.get('name', user_info.name)
        user_info.phone = request.POST.get('phone', user_info.phone)
        user_info.age = request.POST.get('age', user_info.age)
        user_info.gender = request.POST.get('gender', user_info.gender)

        if 'avatar' in request.FILES:
            user_info.avatar = request.FILES['avatar']

        user_info.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '个人信息更新成功'
            })
        return redirect('bill:profile')  # Add redirect for normal form submit

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
        messages.error(request, f'更新失败: {str(e)}')
        return redirect('bill:profile')
@login_required
@require_http_methods(["POST"])
def change_password(request):
    """修改密码"""
    try:
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # 验证旧密码
        if not check_password(old_password, user.password):
            return JsonResponse({
                'success': False,
                'message': '原密码不正确'
            })

        # 验证新密码
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': '两次输入的新密码不一致'
            })

        # 验证新密码长度和复杂度
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': '新密码长度不能小于8位'
            })

        # 更新密码
        user.set_password(new_password)
        user.save()

        # 更新session，防止被登出
        update_session_auth_hash(request, user)

        return JsonResponse({
            'success': True,
            'message': '密码修改成功，请重新登录'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@require_http_methods(["POST"])
def delete_account(request):
    """注销账号"""
    try:
        user = request.user
        # 先删除用户信息
        UserImformation.objects.filter(user=user).delete()
        # 再删除用户账号
        user.delete()

        return JsonResponse({
            'success': True,
            'message': '账号已成功注销'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def logout_view(request):
    """退出登录"""
    logout(request)
    return redirect('bill:login')