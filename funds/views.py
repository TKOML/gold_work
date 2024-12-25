from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import FundsNetvalue,FundMain,Recommendfunds
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from plotly.offline import plot
import plotly.graph_objects as go
import numpy as np

# Create your views here.
def index(request):
    fundsvalue = FundsNetvalue.objects.filter(day='2021-11-11T00:00:00Z')
    paginator = Paginator(fundsvalue, 10)  # 每页显示10个基金
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是一个整数就返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页数超出总页数就返回最后一页
        posts = paginator.page(paginator.num_pages)
    recomm = Recommendfunds.objects.all()
    context = {
        'recommendfunds':recomm,
        'fundsvalues':posts,
        'page':page,
    }
    return render(request,'funds/index.html',context)



def fund_info(request,code_id):
    fund_main = get_object_or_404(FundMain, main_code=code_id)
    fund_values = FundsNetvalue.objects.filter(code=code_id)
    fundvalue_last = fund_values.last()
    fund_day = [i.day.strftime("%Y-%m-%d") for i in fund_values]
    fund_netvalue = [round(i.net_value,2) for i in fund_values]
    fund_sumvalue = [round(i.sum_value,2) for i in fund_values]
    fund_totalreturn = [round(i.total_return,2) for i in fund_values]

    def fund_line(fund_x,fund_y):

        trace = go.Scatter(
		    x = fund_x,
		    y = fund_y,
            mode="lines",
            fill='tozeroy'
  	    )
	
        layout = dict(
            showlegend=False,
            autosize=False,
            width=800,
            height=500,
            margin=dict(
               t=20,
               l=10,
               r=10,
               b=10
            ),
            hovermode='closest',            
		    xaxis = dict(range=[min(fund_x),max(fund_x)]),
		    yaxis = dict(range=[min(fund_y),max(fund_y)])
	    )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        return plot_div 

    context = {
        'fundmain':fund_main,
        'fundvalues':fund_values,
        'fundvalues_last':fundvalue_last,
        'fund_netvalue_line':fund_line(fund_day,fund_netvalue),
        'fund_sumvalue_line':fund_line(fund_day,fund_sumvalue),
        'fund_totalreturn_line':fund_line(fund_day,fund_totalreturn),   
    }

    return render(request,'funds/fund_info.html',context) 


