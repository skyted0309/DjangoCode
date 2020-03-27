import pandas as pd
import matplotlib
from matplotlib.font_manager import *
import matplotlib.pyplot as plt
import math
import shutil
import os

def empty_dir(path):
    file_list = os.listdir(path)
    if len(file_list) != 0:
        for each_file in file_list:
            os.remove(path + '/' + each_file)

def roomtype_month_price(final_name, channel, roomtype, num):
    title = roomtype + '-(' + channel + ')'# 圖片標題使用。
    realtime_info = pd.read_csv('../hotelproject/hotelinfo_app/all_realtime_universal_naming.csv') # 讀檔
    # 塞選條件(飯店名稱、通路、房型、1號到31號。)
    final_name = realtime_info["final_name"] == final_name
    channel = realtime_info['channel'] == channel
    roomtype = realtime_info['roomtype'] == roomtype
    date_list = []
    price_list = []
    for i in range(1, 32):
        date = (i)
        date_list.append(date)
        try:
            checkin = realtime_info['checkin'] == '2020/3/%d' % (i)
            date_price = realtime_info[(final_name) & (channel) & (roomtype) & (checkin)].price.values[0]
            price_list.append(date_price)
        except: # 如果當天沒有價格就填0
            price_list.append(0)
            pass
    # ==============================================
    highest_price = max(price_list) # 最高價
    lowest_price = min(each_price for each_price in price_list if each_price > 0) # 最低價
    highest_price_set_range = (math.ceil(highest_price /1000)) * 1000 # 設定顯示區間用

    # x軸、y軸設定
    x = date_list # x軸
    y = price_list # y軸

    # ==============================================
    # 設定顏色
    colors = []
    for each_date_price in price_list:
        if each_date_price == highest_price:
            colors.append('red')
        elif each_date_price == lowest_price:
            colors.append('green')
        else:
            colors.append('gold')
    # ==============================================
    plt.figure(figsize=(30, 10))  # 畫布大小

    plt.xticks(x, fontsize = 30)  # x軸刻度
    yy = range(500, highest_price_set_range + 1000, 1000) # 最高的價格、以1000為區間
    plt.yticks(yy, fontsize = 30)  # y軸刻度
    plt.bar(x, y, align='center', linewidth=5, color=colors)
    myfont = FontProperties(fname = '../hotelproject/hotelinfo_app/msjhbd.ttc')
    plt.title(title, fontproperties = myfont, fontsize = 30) # 設定標題跟字體(微軟正黑體)。

    plt.xlabel("date", fontsize = 30) # X軸標籤
    plt.ylabel('price', fontsize = 30) # y軸標籤
    return plt.savefig('../hotelproject/hotelinfo_app/static/price_photo_images/{}.png'.format(num))