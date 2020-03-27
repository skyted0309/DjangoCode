from sqlalchemy import create_engine
import pandas as pd
from hotelinfo_app.price_photo import roomtype_month_price, empty_dir

def mysql_page2_finalname_total_selecttag(city, checkin, checkout, roomtype, available, tag_list):
    sql_tag_total = ''  # 拿來下SQL的
    service_point = 0
    food_point = 0
    facility_point = 0
    traffic_point = 0
    clean_point = 0
    for eachtag in tag_list:  # 判斷出使用者選的標籤。
        if eachtag == 'service':
            service_point = 0.5
            sql_tag_total += eachtag + '+'
        elif eachtag == 'food':
            food_point = 0.5
            sql_tag_total += eachtag + '+'
        elif eachtag == 'facility':
            facility_point = 0.5
            sql_tag_total += eachtag + '+'
        elif eachtag == 'traffic':
            traffic_point = 0.5
            sql_tag_total += eachtag + '+'
        elif eachtag == 'clean':
            clean_point = 0.5
            sql_tag_total += eachtag + '+'
    connect = create_engine(
        'mysql+pymysql://{}:{}@{}:{}/{}'.format('root', 'root', '104.199.227.211', '3306', 'goodgo'))
    sql_code = '''select final_name, round(avg({}), 2) as total, round(avg(price), 0) as average from (
        SELECT * FROM goodgo.final_info
        where city = '{}' and people = {} and available >= {}
        and service >= {} and food >= {} and facility >= {} and traffic >= {} and clean >= {}
        and checkin BETWEEN '{}' AND '{}') as a
        group by final_name
        order by total DESC 
        limit 20'''.format(sql_tag_total[:-1], city, roomtype, available, service_point, food_point,
                                      facility_point, traffic_point, clean_point, checkin, checkout)

    page2_result = pd.read_sql_query(sql_code, connect)
    print(sql_code)
    return page2_result

def mysql_page3_hotel_basicinfo(final_name, city, roomtype, available, checkin, checkout):
    connect = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format('root', 'root', '104.199.227.211', '3306', 'goodgo'))
    sql_code = '''select final_name, address, longitude, latitude, service, facility, clean, food, traffic from (
    SELECT * FROM goodgo.final_info
    where final_name = "{}" and city = '{}' and people = {} and available >= {}) as search_result
    where checkin BETWEEN '{}' AND '{}'
    limit 1'''.format(final_name, city, roomtype, available, checkin, checkout)
    page3_hotel_basicinfo_result = pd.read_sql_query(sql_code, connect)
    return page3_hotel_basicinfo_result

def mysql_page3_roomtype_total_price(final_name, city, roomtype, available, checkin, checkout):
    connect = create_engine(
        'mysql+pymysql://{}:{}@{}:{}/{}'.format('root', 'root', '104.199.227.211', '3306', 'goodgo'))
    sql_code = '''select roomtype, channel, sum(price) as price, url from(
    select concat(final_name, roomtype, channel) as groupby , final_name, roomtype, channel, price, checkin, url
    from goodgo.final_info
    where final_name = '{}'and city = '{}' and people = {} and available >= {} and  checkin BETWEEN '{}' and '{}') as unusedbutmust
       group by groupby
       order by price ASC '''.format(final_name, city, roomtype, available, checkin, checkout)
    roomtype_all_info = pd.read_sql_query(sql_code, connect)
    roomtype_list = roomtype_all_info['roomtype'].unique().tolist()

    all_roomtype_info_list = []
    for each_roomtype in roomtype_list:
        fliter = (roomtype_all_info['roomtype'] == each_roomtype)
        each_roomtype_info = roomtype_all_info[fliter]
        each_roomtype_info_list = []

        for row in each_roomtype_info.itertuples(index=True, name='Pandas'):  # 一個房間有幾個通路就做幾本字典。
            info_dict = {'channel': row[2], 'price': int(row[3]), 'url': row[4]}
            each_roomtype_info_list.append(info_dict)

        each_roomtype_dict = {'roomtype': each_roomtype, 'info': each_roomtype_info_list}
        all_roomtype_info_list.append(each_roomtype_dict)

    # 每個房型價格走勢圖
    empty_dir('../hotelproject/hotelinfo_app/static/price_photo_images') # 先清空圖片資料夾
    for num, each_roomtype_photo in enumerate(all_roomtype_info_list):
        roomtype_month_price(final_name= final_name, channel = each_roomtype_photo['info'][0]['channel'], roomtype=each_roomtype_photo['roomtype'], num = num)
    return all_roomtype_info_list