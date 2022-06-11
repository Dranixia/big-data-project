import requests
import pprint
import json


class Client:
    def __init__(self, url):
        self.url = url
        self.queries = {
            1: [],
            2: ["user_id"],
            3: ["domain"],
            4: ["page_id"],
            5: ["start", "end"],
            6: []
        }

    def get_request(self, query_number):

        query_body = {
            "query_number": query_number,
            "params": {}
        }
        if query_number <= 0 or query_number >= 7:
            return None
        else:
            for param in self.queries[query_number]:
                value = input("Enter %s: " % param)
                query_body["params"][param] = value
            return query_body

    def send_query(self, query_body):
        response = requests.get(self.url, json=query_body)
        return response.status_code, response.json()


def main():
    client = Client('http://localhost:8085')
    while True:
        query_number = int(input("1: Return all domains\n"
                                 "2: Return all pages created by *user_id*\n"
                                 "3: Return number of articles for a *domain*\n"
                                 "4: Return uri with *page_id*\n"
                                 "5: Return name, id, and number of pages created for all users between *start_time* and *end_time* (format: only YYYY-MM-DD HH:MM:SS)\n"
                                 "6: Return Category A response\n"
                                 "0: Exit\n"))

        query_body = client.get_request(query_number)

        if query_body is None:
            break
        else:
            _, js = client.send_query(query_body)
            pprint.pprint(js)
            with open(f"json_res{query_number}.json", "w", encoding="utf-8") as f:
                json.dump(js, f)


if __name__ == "__main__":
    main()
