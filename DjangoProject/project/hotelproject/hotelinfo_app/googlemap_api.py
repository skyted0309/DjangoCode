import googlemaps
from datetime import datetime

class googlemap_api:
    def __init__(self, key):
        self.api_key = key  # 宣告金鑰變成全域鑰匙
        self.output_list = []
        self.gmaps_key = googlemaps.Client(key=self.api_key)

    def google_api_return_destination_distance_traffictime(self, latitude, longitude): # 經度、緯度、類型(選擇你要捷運站 or 火車站 or機場) https://developers.google.com/places/supported_types?hl=zh-tw
        self.setting_place ='{},{}'.format(latitude,longitude)
        type_list = ['airport', 'train_station', 'subway_station'] # type_list : 火車、飛機、捷運
        airport_list = ['台北松山機場', '台灣桃園國際機場']

        for each_type in type_list:
            if each_type == 'airport':
                for target_name in airport_list:
                    target_name = target_name
                    each_output = self.google_api_directions_result(target_name) # 去拿地點、距離、時間的字典
                    self.output_list.append(each_output)

            else: # 跑火車站跟捷運站。
                radius = 1000
                while True: # 半徑1000有時會沒車站跟捷運站
                    try:
                        setting_place_info = self.gmaps_key.places_nearby(
                            location = self.setting_place,
                            radius = radius,  # 為了機場，設定10000
                            language = "zh-TW",
                            type = each_type)
                        target_name = setting_place_info['results'][0]['name']
                        self.google_api_directions_result(target_name)
                        break
                    except:
                        radius += 1000
                each_output = self.google_api_directions_result(target_name) # 去拿地點、距離、時間的字典
                self.output_list.append(each_output)
        return self.output_list

    def google_api_directions_result(self, target_name):
        now = datetime.now()
        directions_result = self.gmaps_key.directions(self.setting_place, # 出發點
                                                     target_name, # 終點
                                                     mode = 'transit',  # driving.walking,bicycling,transit
                                                     avoid = 'none',  # tolls,highways,ferries,indoor
                                                     # transit_mode = "bus,subway,train,tram,rail",
                                                     # transit_routing_preference = "less_walking,fewer_transfers"
                                                     language = "zh-TW",
                                                     departure_time = now)
        distance = directions_result[0]['legs'][0]['distance']['text'].replace(' ','')
        traffictime = directions_result[0]['legs'][0]['duration']['text'].replace(' ','')
        each_output = {'name': target_name, 'distance': distance, 'traffictime':traffictime}
        return each_output