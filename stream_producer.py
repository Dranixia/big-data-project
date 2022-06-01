import requests
from kafka import KafkaProducer
import json


class KafkaWriter:
    def __init__(self, kafka_host, topic_name):
        self.producer = KafkaProducer(bootstrap_servers=kafka_host, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = topic_name

    def make_data(self):
        r = requests.get('https://stream.wikimedia.org/v2/stream/page-create', stream=True)

        if r.encoding is None:
            r.encoding = 'utf-8'

        for line in r.iter_lines(decode_unicode=True):
            if line and line.split()[0] == "data:":
                line = line[5:]
                jd = json.loads(line)
                self.producer.send(self.topic, jd)

    def produce(self):
        while True:
            # r.iter_lines() fails sometimes, so we just go again
            try:
                self.make_data()
                break
            except:
                pass


def main():
    kafka_tweets = KafkaWriter("kafka-server:9092", "wiki")
    kafka_tweets.produce()


if __name__ == "__main__":
    main()
