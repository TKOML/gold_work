
from django.db import models


class UserImformation(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=20, primary_key=True)
    password = models.CharField(verbose_name='密码', max_length=16)
    phone = models.CharField(verbose_name='手机号', max_length=11)
    age = models.IntegerField(verbose_name="年龄")
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices)


class BillOutcome(models.Model):  # 支出表
    belong_out = models.CharField(verbose_name="姓名",max_length=20)
    time_out = models.DateTimeField(verbose_name="时间")  # 时间
    account_choices_out = (
        (1, "微信"),
        (2, "支付宝"),
        (3, "现金"),
        (4, "银行卡"),
        (5, "信用卡"),
    )
    account_type_out = models.SmallIntegerField(verbose_name="账户", choices=account_choices_out)  # 账户
    classify_choices_out = (
        (1, "餐饮"),
        (2, "交通"),
        (3, "购物"),
        (4, "居家"),
        (5, "娱乐"),
        (6, "人情"),
        (7, "医疗"),
        (8, "金融"),
        (9, "其他"),
    )
    classify_type_out = models.SmallIntegerField(verbose_name="类别", choices=classify_choices_out)  # 类型
    money_out = models.DecimalField(verbose_name="金额", max_digits=10, decimal_places=2)  # 金额
    notes_out = models.CharField(verbose_name="备注", max_length=1000, blank=True, null=True)  # 备注


class BillIncome(models.Model):   # 收入表
    belong_in = models.CharField(verbose_name="姓名",max_length=20)
    time_in = models.DateTimeField(verbose_name="时间")  # 时间
    account_choices_in = (
        (1, "微信"),
        (2, "支付宝"),
        (3, "现金"),
        (4, "银行卡"),
        (5, "金融"),
    )
    account_type_in = models.SmallIntegerField(verbose_name="账户", choices=account_choices_in)  # 账户
    classify_choices_in = (
        (1, "工资"),
        (2, "兼职"),
        (3, "经营"),
        (4, "利息"),
        (5, "奖金"),
        (6, "加班"),
        (7, "基金"),
        (8, "股票"),
        (9, "债券"),
        (10, "其他"),
    )
    classify_type_in = models.SmallIntegerField(verbose_name="类别", choices=classify_choices_in)  # 类型
    money_in = models.DecimalField(verbose_name="金额", max_digits=10, decimal_places=2)  # 金额
    notes_in = models.CharField(verbose_name="备注", max_length=1000, blank=True, null=True)  # 备注
