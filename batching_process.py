import datetime
from cassandra.cluster import Cluster
from kafka import KafkaConsumer, TopicPartition
import json
import uuid

from pyspark.sql import SparkSession
from pyspark.sql import functions as fn


def get_current_interval():
    return datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)


class CassandraClient:
    def __init__(self, host, port, keyspace):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.session = None
        self.spark = SparkSession.builder.appName("Project").getOrCreate()
        self.df = self.spark.read.load("wikidata.csv", format="csv", inferSchema=True, multiline=True, header=True)

        self.a1 = []
        self.a2 = {}
        self.a3 = {}

    def connect(self):
        cluster = Cluster([self.host], port=self.port)
        self.session = cluster.connect(self.keyspace)

    def execute(self, query):
        self.session.execute(query)

    def add_row_df(self, dt, domain, page_title, user_name, user_id, is_bot, interval):
        columns = ["time", "domain", "page_title", "user_name", "user_id", "is_bot", "interval"]
        vals = [dt, domain, page_title, user_name, user_id, is_bot, interval]
        local = self.spark.createDataFrame(vals, columns)
        self.df = self.df.union(local)

    def write(self, domain, dt, page_id, page_title, uri, user_name, user_id, is_bot, interval):
        self.add_row_df(dt, domain, page_title, user_name, user_id, is_bot, interval)

        query1 = "INSERT INTO domains_and_articles (domain, uri)" \
                 " VALUES ('%s','%s')" % (domain, uri)

        query2 = "INSERT INTO user_pages (user_id, uri)" \
                 " VALUES (%s, '%s')" % (user_id, uri)

        query3 = "INSERT INTO pages (page_id, uri)" \
                 " VALUES (%s, '%s')" % (page_id, uri)

        query4 = "INSERT INTO user_dates (user_id, user_name, uri, dt)" \
                 " VALUES (%s, '%s', '%s', '%s')" % (user_id, user_name, uri, dt)

        self.execute(query1)
        self.execute(query2)
        self.execute(query3)
        self.execute(query4)

    def update_category_a(self):
        old_hour = get_current_interval() - datetime.timedelta(hours=8)
        self.df = self.df.filter(self.df.interval != datetime.datetime.strftime(old_hour, "%Y-%m-%d %H:%M:%S"))

        if len(self.a1) == 6:
            self.a1 = self.a1[1:]
        self.a1.append()

    def get_new_a1(self):
        local = self.df.filter(self.df.interval == datetime.datetime.strftime(get_current_interval()-datetime.timedelta(hours=2), "%Y-%m-%d %H:%M:%S")).groupBy(self.df)

    def get_new_a2(self):
        pass

    def get_new_a3(self):
        pass


class KafkaReader:
    def __init__(self, kafka_host, topic_name, cassandra_host, cassandra_port, keyspace):
        self.consumer = KafkaConsumer(bootstrap_servers=kafka_host)
        self.consumer.assign(
            [TopicPartition(topic_name, 1), TopicPartition(topic_name, 2), TopicPartition(topic_name, 3)])
        self.client = CassandraClient(cassandra_host, cassandra_port, keyspace)
        self.client.connect()

    def read(self):
        current_interval = get_current_interval()
        while True:
            if current_interval != get_current_interval():
                self.client.update_category_a()

            jd = json.loads(next(self.consumer).value.decode('utf-8'))

            domain = jd["meta"]["domain"]
            dt = jd["meta"]["dt"].replace("T", " ").replace("Z", "")
            page_id = jd["page_id"]
            uri = jd["meta"]["uri"]
            page_title = jd["page_title"]
            user_name = jd["performer"]["user_text"]
            # If the user_name is an IP, there will be no user_id in data
            try:
                user_id = jd["performer"]["user_id"]
            except KeyError:
                user_id = 0
            is_bot = jd["performer"]["user_is_bot"]
            interval = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(minute=0, second=0)
            self.client.write(domain, dt, page_id, page_title, uri, user_name, user_id, is_bot, interval)


def main():
    kafka_tweets = KafkaReader("kafka-server:9092", "wiki", 'cassandra-node', 9042, 'wikidata')
    kafka_tweets.read()


if __name__ == "__main__":
    main()
