import requests
import datetime
import re
import plotly.offline as opy
import plotly.graph_objs as go
import os
import plotly.express as px
import pandas as pd
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.express as px

#magic for date




def graph(request):
    x_data = [0,1,2,3]
    y_data = [x**2 for x in x_data]
    plot_div = plot([Scatter(x=x_data, y=y_data,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='green')],
               output_type='div')
    return render(request, "index.html", context={'plot_div': plot_div})



"""def graph(request):

    vendors = ["Цифровая экономика", "Малое и среднее предпринимательство", "Производительность труда",
               "Международная кооперация и экспорт", "Экология", "Образование", "Наука", "Культура", "Здравоохранение",
               "Жилье и городская среда", "Демография", "Безопасные и качественные автомобильные дороги",
               "Транспортная инфраструктура"]
    sectors = ["Национальная экономика", "Национальная экономика", "Национальная экономика", "Национальная экономика",
               "Охрана окружающей среды", "Образование", "Образование", "Культура, кинематография", "Здравоохранение",
               "Социальная политика", "Социальная политика", "Социальная политика", "Социальная политика"]
    regions = ["Национальные проекты", "Национальные проекты", "Национальные проекты", "Национальные проекты",
               "Национальные проекты", "Национальные проекты", "Национальные проекты", "Национальные проекты",
               "Национальные проекты", "Национальные проекты", "Национальные проекты", "Национальные проекты",
               "Национальные проекты"]
    df = pd.DataFrame(
        dict(vendors=vendors, sectors=sectors, regions=regions)
    )
    print(df)
    fig = px.sunburst(df, path=['regions', 'sectors', 'vendors'])
    context['graph'] = div

    return context"""



def get_Info(request):

    if request.method == 'POST' and request.POST['salary'] != '':
        region = request.POST['region']
        salary = request.POST['salary']
        period = 0

        date = '2016-15-07'
        tax = int(salary) * 0.13



        # magic for date
        now = datetime.datetime.now()
        date_second = now.strftime("%d.%m.%Y")
        date_first = date_second[:8] + str(int(date_second[7:]) - 10)

        date_for_url = date_first + '-' + date_second
        print(date_for_url)

        # converting a region to a code
        region_base = pd.read_csv(os.getcwd()+'/audithon/static/assets/csv/codes.csv', index_col='region')
        # print(region_base)
        kod_for_url = str(region_base.loc[region, 'kod'])
        if len(kod_for_url) == 1:
            kod_for_url = '0' + kod_for_url

        # creating url_api by region and price
        url = 'https://api.spending.gov.ru/v1/contracts/search/?currentstage=EC&customerregion='
        reg_for_url = kod_for_url
        date_url = '&daterange='
        api = url + str(reg_for_url) + date_url + date_for_url
        print(api)

        # text from api
        contracts_get_api = requests.get(api)
        contracts_text = contracts_get_api.json()

        test = contracts_text['contracts']['data']
        df = pd.DataFrame(test)

        if 'economic_sectors' in df.columns:
            df = df.dropna(axis='index', how='any', subset=['economic_sectors'])
            df = df.reset_index(drop=True)

        # create dataframe2
        paid = tax / df.loc[:, 'price'] * 100
        paidk = tax / df.loc[:, 'price'] * 100 * 3
        paidy = tax / df.loc[:, 'price'] * 100 * 12

        if 'economic_sectors' in df.columns:
            economic_sectors = []
            for i in range(len(df)):
                economic_sectors.append(df.loc[i, 'economic_sectors'][0]['title'])

        customer = []
        for i in range(len(df)):
            customer.append(df.loc[i, 'customer']['fullName'])

        name = []
        for i in range(len(df)):
            name.append(df.loc[i, 'products'][0]['name'])

        contract_info = pd.DataFrame()

        if 'contractUrl' in df.columns:
            contract_info = df[['contractUrl', 'price']]
        else:
            contract_info = df[['price']]

        contract_url = []
        for i in range(len(contract_info)):
            contract_url.append('<td onclick = "document.location=\''+contract_info['contractUrl'][i]+"'"+'">'+contract_info['contractUrl'][i]+'< / td >')



        contract_info['contractUrl'] = contract_url
        contract_info['name_of_products'] = name
        if 'economic_sectors' in df.columns:
            contract_info['economic_sectors'] = economic_sectors
        contract_info['customer'] = customer
        contract_info['paid'] = paid
        contract_info['paid_k'] = paidk
        contract_info['paid_y'] = paidy

        contract_info = contract_info[contract_info['paid_y'] < 100].sort_values(by=['price'],
                                                                                 ascending=False).reset_index(drop=True)

        fin_table = contract_info
        fin_table.columns = ["Ссылка на контракт", "Стоимость, руб", "Наименование услуги/продукта",
                             "Экономический сектор", "Заказчик", "Ваш вклад за месяц, %", "Ваш вклад за квартал, %",
                             "Ваш вклад за год,%"]

        tax_month = tax
        tax_cvartal = tax * 3
        tax_year = tax * 12

        taxes = {'tax_month': tax_month, 'tax_cvartal': tax_cvartal, 'tax_year': tax_year}

        table0 = {'table': [contract_info.to_html(classes='data')], 'titles': contract_info.columns.values}
        table = {'table': fin_table.to_html(), 'tax_month': tax_month}
        context = {'graph': graph}

    elif request.POST['salary'] == '':
        table = {}
    return render(request, 'index.html', table)


