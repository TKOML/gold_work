import csv
import json
import random
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Portfolio, FundHolding
from funds.models import FundMain,FundsNetvalue
#import jqdatasdk as jq

@login_required
def dashboard(request):
    try:
      portfolio = Portfolio.objects.get(user=request.user)
    except:
      portfolio = Portfolio.objects.create(user=request.user)
    portfolio.update_investment()
    holding_funds = FundHolding.objects.filter(portfolio=portfolio)
    holdings = []
    sectors = [[], []]
    sector_wise_investment = {}
    funds = [[], []]
    for c in holding_funds:
      fund_symbol = c.fund_symbol
      fund_name = c.fund_name
      number_shares = c.number_of_shares
      investment_amount = c.investment_amount
      average_cost = investment_amount / number_shares
      holdings.append({
        'FundSymbol': fund_symbol,
        'FundName': fund_name,
        'NumberShares': number_shares,
        'InvestmentAmount': investment_amount,
        'AverageCost': average_cost,
      })
      funds[0].append(round((investment_amount / portfolio.total_investment) * 100, 2))
      funds[1].append(fund_symbol)
      if c.sector in sector_wise_investment:
        sector_wise_investment[c.sector] += investment_amount
      else:
        sector_wise_investment[c.sector] = investment_amount
    for sec in sector_wise_investment.keys():
      sectors[0].append(round((sector_wise_investment[sec] / portfolio.total_investment) * 100, 2))
      sectors[1].append(sec)

    context = {
      'holdings': holdings,
      'totalInvestment': portfolio.total_investment,
      'funds': funds,
      'sectors': sectors,
    }

    return render(request, 'myfunds/dashboard.html', context)

def add_holding(request):
  if request.method == "POST":
    try:
      portfolio = Portfolio.objects.get(user=request.user)
      holding_funds = FundHolding.objects.filter(portfolio=portfolio)
      fund_symbol = request.POST['fund'].split('(')[1].split(')')[0]
      fund_name = request.POST['fund'].split('(')[0].strip()
      number_funds = int(request.POST['number-funds'])     
      # fund_net_value = jq.finance.run_query(jq.query(jq.finance.FUND_NET_VALUE).
      #                                 filter(jq.finance.FUND_NET_VALUE.code==fund_symbol,
      #                                        jq.finance.FUND_NET_VALUE.day==request.POST['date']))
      # buy_price = fund_net_value.iloc[0].at['sum_value']  
      fund_net_value = FundsNetvalue.objects.filter(code=fund_symbol,day=request.POST['date'] ).values('sum_value').first()
      buy_price = float(fund_net_value['sum_value'])                                          
      # fund_main = jq.finance.run_query(jq.query(jq.finance.FUND_MAIN_INFO).
      #                                filter(jq.finance.FUND_MAIN_INFO.main_code==fund_symbol))                                   
      # sector = fund_main.iloc[0].at['invest_style']
      print('add buy price:',buy_price)
      fund_main = FundMain.objects.filter(main_code=fund_symbol).values('underlying_asset_type').first()                              
      sector = fund_main['underlying_asset_type']      
      print("sector:",sector)
      print("number_funds:",number_funds)
      found = False
      for c in holding_funds:
        if c.fund_symbol == fund_symbol:
          c.buying_value.append([buy_price, number_funds])
          c.save()
          found = True
       
      if not found:
        c = FundHolding.objects.create(
          portfolio=portfolio, 
          fund_name=fund_name, 
          fund_symbol=fund_symbol,
          number_of_shares=number_funds,
          sector=sector
        )
        c.buying_value.append([buy_price, number_funds])
        c.save()
      print("success")
      return HttpResponse("Success")
    except Exception as e:
      print("error:",e)
      return HttpResponse(e)

def send_fund_list(request):
  funds_data = FundMain.objects.all()
  rows = [[item.main_code,item.name] for item in funds_data]
  return JsonResponse({"data": rows})

def update_values(request):
  try:
    portfolio = Portfolio.objects.get(user=request.user)
    current_value = 0
    unrealized_pnl = 0
    growth = 0
    holding_funds = FundHolding.objects.filter(portfolio=portfolio)
    funddata = {}
    for c in holding_funds:
      # fund_net_value = jq.finance.run_query(jq.query(jq.finance.FUND_NET_VALUE).
      #                                 filter(jq.finance.FUND_NET_VALUE.code==c.fund_symbol).order_by(jq.finance.FUND_NET_VALUE.day.desc()).limit(1))
      # last_trading_price = fund_net_value.iloc[0].at['sum_value']
      print("c",c)
      fund_net_value = FundsNetvalue.objects.filter(code=c.fund_symbol).order_by('-day').values('sum_value').first()      
      last_trading_price = float(fund_net_value['sum_value'])      
      print("last_trading_price",last_trading_price)
      pnl = (last_trading_price * c.number_of_shares) - c.investment_amount
      print("pnl",pnl)
      net_change = pnl / c.investment_amount
      funddata[c.fund_symbol] = {
        'LastTradingPrice': last_trading_price,
        'PNL': pnl,
        'NetChange': net_change * 100
      }
      current_value += (last_trading_price * c.number_of_shares)
      unrealized_pnl += pnl
    growth = unrealized_pnl / portfolio.total_investment
    return JsonResponse({
      "FundData": funddata, 
      "CurrentValue": current_value,
      "UnrealizedPNL": unrealized_pnl,
      "Growth": growth * 100
    })
  except Exception as e:
    return JsonResponse({"Error": str(e)})