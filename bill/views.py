import datetime
import json

from django.shortcuts import render, redirect,HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from bill import models
from bill.utils.page import Pagination
from django.http import JsonResponse


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

        return redirect("/bill/zzbill")
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
        return redirect('/bill/login')

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
        return redirect('/bill/zzbill/outcome/list')
    return render(request, 'outcome_add.html', {"form": form})


def outcome_edit(request, nid):
    row = models.BillOutcome.objects.filter(id=nid).first()
    if request.method == "GET":
        form = OutcomeModelForm(instance=row)
        return render(request, 'outcome_edit.html', {"form": form})
    form = OutcomeModelForm(data=request.POST, instance=row)
    if form.is_valid():
        form.save()
        return redirect('/bill/zzbill/outcome/list')
    return render(request, 'outcome_edit.html')


def outcome_delete(request, nid):
    models.BillOutcome.objects.filter(id=nid).delete()
    return redirect('/bill/zzbill/outcome/list')


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
        return redirect('/bill/zzbill/income/list')
    return render(request, 'income_add.html', {"form": form})


def income_edit(request, nid):
    row = models.BillIncome.objects.filter(id=nid).first()
    if request.method == "GET":
        form = IncomeModelForm(instance=row)
        return render(request, 'income_edit.html', {"form": form})
    form = IncomeModelForm(data=request.POST, instance=row)
    if form.is_valid():
        form.save()
        return redirect('/bill/zzbill/income/list')
    return render(request, 'income_edit.html')


def income_delete(request, nid):
    models.BillIncome.objects.filter(id=nid).delete()
    return redirect('/bill/zzbill/income/list')


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



