from confluent_kafka import Producer, Consumer
from elasticsearch import Elasticsearch, helpers
import json


class kafka_connect:
    def __init__(self, ip_port):
        self.ip_port = ip_port # xx.xxx.xxx.xxx:9092 xxx自己kafka的IP

    # 轉換msgKey或msgValue成為utf-8的字串
    def try_decode_utf8(self, data):
        if data:
            return data.decode('utf-8')
        else:
            return None

    # 當發生Re-balance時, 如果有partition被assign時被呼叫
    def print_assignment(self, consumer, partitions):
        result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
        print('Setting newly assigned partitions:', result)

    # 當發生Re-balance時, 之前被assigned的partition會被移除
    def print_revoke(self, consumer, partitions):
        result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
        print('Revoking previously assigned partitions: ' + result)

    def kafka_producer(self, kafka_value):
        value = json.dumps(kafka_value, ensure_ascii=False)
        # 步驟1. 設定要連線到Kafka集群的相關設定
        props = {
            # Kafka集群在那裡?
            'bootstrap.servers': self.ip_port  # <-- 置換成要連接的Kafka集群
        }
        # 步驟2. 產生一個Kafka的Producer的實例
        producer = Producer(props)
        # 步驟3. 指定想要發佈訊息的topic名稱
        topicName = 'search_log'
        # produce(topic, [value], [key], [partition], [on_delivery], [timestamp], [headers])
        producer.produce(topicName, value=value)
        # 步驟5. 確認所在Buffer的訊息都己經送出去給Kafka了
        producer.flush()

    def kafka_consumer(self):
        props = {
            'bootstrap.servers': self.ip_port,  # Kafka集群在那裡? (置換成要連接的Kafka集群)
            'group.id': 'goodgo',
            'auto.offset.reset': 'earliest',  # Offset從最前面開始
        }
        # 步驟2. 產生一個Kafka的Consumer的實例
        consumer = Consumer(props)
        # 步驟3. 指定想要訂閱訊息的topic名稱
        topicName = 'search_log'
        # 步驟4. 讓Consumer向Kafka集群訂閱指定的topic
        consumer.subscribe([topicName], on_assign=self.print_assignment, on_revoke=self.print_revoke)
        count = 0 # 紀錄筆數
        while True:
            records = consumer.consume(num_messages=500, timeout=1.0)  # 批次讀取
            if len(records) > 0:
                count += 1
                for record in records:
                    topic = record.topic()
                    partition = record.partition()
                    offset = record.offset()
                    # 取出msgKey與msgValue
                    msgKey = self.try_decode_utf8(record.key())
                    msgValue = self.try_decode_utf8(record.value())

                # 秀出metadata與msgKey & msgValue訊息
                print('%s-%d-%d : (%s , %s)' % (topic, partition, offset, msgKey, msgValue))
                savedata_els(http_ip_port='http://35.221.163.250:9200', count=count, msgValue=msgValue)


def savedata_els(http_ip_port, msgValue, count):
    els_save_data = json.loads(msgValue)
    city = els_save_data[0]
    checkin = els_save_data[1]
    checkout = els_save_data[2]
    roomtype = els_save_data[3]
    available = els_save_data[4]

    tag_list = els_save_data[5]
    service = 0
    food = 0
    facility = 0
    traffic = 0
    clean = 0
    for eachtag in tag_list:  # 判斷出使用者選的標籤。
        if eachtag == 'service':
            service = 1
        elif eachtag == 'food':
            food = 1
        elif eachtag == 'facility':
            facility = 1
        elif eachtag == 'traffic':
            traffic = 1
        elif eachtag == 'clean':
            clean = 1
    es = Elasticsearch(http_ip_port)
    actions = []
    action = {
        "_index": "search",
        "_type": "search",
        "_id": count,
        "_source": {
            u"city": city,
            u"checkin": checkin,
            u"checkout": checkout,
            u"roomtype": roomtype,
            u"available": available,
            u"service": service,
            u"food": food,
            u"facility": facility,
            u"traffic": traffic,
            u"clean": clean
        }
    }
    actions.append(action)

    if (len(actions) == 1):
        helpers.bulk(es, actions)
        print('successful')
        del actions[0:len(actions)]

if __name__ == '__main__':
    kafka = kafka_connect(ip_port='35.221.163.250:9092')
    while True:
        kafka.kafka_consumer()