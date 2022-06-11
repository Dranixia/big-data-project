from cassandra.cluster import Cluster
from flask import jsonify, request, Flask


class CassandraClient:
    def __init__(self, host, port, keyspace):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.session = None

    def connect(self):
        cluster = Cluster([self.host], port=self.port)
        self.session = cluster.connect(self.keyspace)

    def execute(self, query):
        self.session.execute(query)

    def query1(self):
        query = "SELECT DISTINCT domain from domains_and_articles"

        rows = self.session.execute(query)
        return rows

    def query2(self, user_id):
        query = "SELECT uri from user_pages WHERE user_id=%s" % user_id

        rows = self.session.execute(query)
        return rows

    def query3(self, domain):
        query = "SELECT COUNT(*) from domains_and_articles WHERE domain='%s'" % domain

        rows = self.session.execute(query)
        return rows

    def query4(self, page_id):
        query = "SELECT uri FROM pages WHERE page_id=%s" % page_id

        rows = self.session.execute(query)
        return rows

    def query5(self, start_date, end_date):
        query = "SELECT user_id, user_name, COUNT(*) FROM user_dates WHERE dt >= '%s' AND" \
                " dt <= '%s' GROUP BY user_id ALLOW FILTERING" % (start_date, end_date)

        rows = self.session.execute(query)
        return rows

    def query6(self):
        query = "SELECT response FROM cat_a"

        rows = self.session.execute(query)
        return rows


class CassandraAPI:

    def __init__(self):
        self.app = Flask(__name__)
        self.client = CassandraClient('cassandra-node', 9042, 'wikidata')
        self.client.connect()

        @self.app.route('/', methods=['GET'])
        def get():
            query = request.get_json()
            return jsonify(self.process_query(query))

    def run(self, host, port):
        self.app.run(host=host, port=port)

    def process_query(self, query_body):
        query_number = int(query_body["query_number"])
        params = query_body["params"]
        rows = []

        if 1 <= query_number <= 6:

            if query_number == 1:
                res = self.client.query1()
                for row in res:
                    rows.append(row.domain)
            elif query_number == 2:
                res = self.client.query2(params["user_id"])
                for row in res:
                    rows.append(row.uri)
            elif query_number == 3:
                res = self.client.query3(params["domain"])
                for row in res:
                    rows.append(row.count)
            elif query_number == 4:
                res = self.client.query4(params['page_id'])
                for row in res:
                    rows.append(row.uri)
            elif query_number == 5:
                res = self.client.query5(params["start"], params["end"])
                for row in res:
                    rows.append([row.user_id, row.user_name, row.count])
            elif query_number == 6:
                res = self.client.query6()
                for row in res:
                    rows.append(row.response)

            return {"rows": rows}


def main():
    app = CassandraAPI()
    app.run("0.0.0.0", 8085)


if __name__ == '__main__':
    main()
