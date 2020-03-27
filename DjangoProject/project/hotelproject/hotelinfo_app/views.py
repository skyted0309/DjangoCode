from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from django.shortcuts import render_to_response
import csv
import datetime as dt
import os
# 自己的python function
from hotelinfo_app.googlemap_api import googlemap_api
from hotelinfo_app.def_mysql import mysql_page2_finalname_total_selecttag, mysql_page3_hotel_basicinfo, mysql_page3_roomtype_total_price
from kafka_els import kafka_connect

def index(request): # page 1: 單純顯示搜尋頁面。
    return render_to_response('index.html',locals())

def resultPage(request): # page 2: 使用者輸入條件，跳出的結果。
    checkin = request.GET.get('checkIn')
    checkout_str = request.GET.get('checkOut')
    d = dt.datetime.strptime(checkout_str, '%Y-%m-%d')
    dd = d + dt.timedelta(days=-1)
    checkout = dd.strftime('%Y-%m-%d')
    roomtype = request.GET.get('room')
    # print(roomtype)
    available = request.GET.get('Rooms')
    tag_list = request.GET.getlist('hoteltag')
    city = request.GET.get('city')
    hotelDataFrame = mysql_page2_finalname_total_selecttag(city, checkin, checkout, roomtype, available, tag_list)
    df = pd.DataFrame(
        data=[{
            'checkin': checkin,
            'checkout': checkout,
            'roomtype': roomtype,
            'available': available,
            'city': city,
            'tag': tag_list}],
        columns=['checkin', 'checkout', 'roomtype', 'available', 'city', 'tag'])
    df.to_csv('query_condition.csv', index=False, encoding='utf-8-sig')  # 產出一張CSV

    advise_hotel_list=[]
    for row in hotelDataFrame.itertuples(index = False, name = 'Pandas'):
        final_score = int(round(float(row[1]) * 100, 0)) // len(tag_list)
        if len(row[0]) < 62:
            hotel={"final_name":row[0],"total":final_score,"average":int(row[2])}
            advise_hotel_list.append(hotel)
    kafka = kafka_connect(ip_port='35.221.163.250:9092')
    kafka_value = [city, checkin, checkout, roomtype, available, tag_list]
    kafka.kafka_producer(kafka_value)
    return render(request,"resultPage.html",locals())

def resultDetail(request): # page 3: 選取飯店的房間資訊
    hotelname = request.GET.get('hotelname')

    with open('query_condition.csv', newline='',encoding='utf-8-sig') as csvfile:
        # 讀取 CSV 檔內容，將每一列轉成一個 dictionary
        rows = csv.DictReader(csvfile)
        checkin = ''
        checkout = ''
        roomtype = ''
        available = ''
        city = ''
        longitude=''
        latitude=''
        # 以迴圈輸出指定欄位
        for row in rows:
            checkin=row['checkin']
            checkout=row['checkout']
            roomtype=row['roomtype']
            available=row['available']
            city=row['city']

    basicinfoDataFrame =mysql_page3_hotel_basicinfo(hotelname, city, roomtype, available, checkin, checkout)

    hotel_basic_list = []
    for row in basicinfoDataFrame.itertuples(index=False, name='Pandas'):
        longitude=row[2]
        latitude=row[3]
        hotel = {"final_name": row[0],
                 "address": row[1],
                 "longitude": row[2], "latitude": row[3],
                 "service": int(round(float(row[4]) * 100, 0)),
                 "facility": int(round(float(row[5]) * 100, 0)),
                 "clean": int(round(float(row[6]) * 100, 0)),
                 "food": int(round(float(row[7]) * 100, 0)),
                 "traffic": int(round(float(row[8]) * 100, 0))}
        hotel_basic_list.append(hotel)
    hotel_price_list=mysql_page3_roomtype_total_price(hotelname, city, roomtype, available, checkin, checkout)
    # print(hotel_price_list)

    googlemap = googlemap_api(key="AIzaSyAphpVUgGh8RUJHQ2VzhgDnBm_S4brGNEs")
    google_api_list = googlemap.google_api_return_destination_distance_traffictime(latitude= float(latitude), longitude=float(longitude))
    # print(google_api_list)
    return render(request, "resultDetail.html", locals())

def price_photo(request):
    file_list = os.listdir('../hotelproject/hotelinfo_app/static/price_photo_images') # 前端HTML用這個list跑迴圈
    return render(request, "price_photo.html", locals())