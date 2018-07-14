# coding: utf-8

import time
from elasticsearch import Elasticsearch

__author__ = "Firas Odeh"
__email__ = "odehfiras@gmail.com"

class Es_connector:

    # def __init__(self, host='localhost', port=9200, user='elastic', password='elastic', timeout=1000, index="test2", doc_type="tweet"):
    def __init__(self, host='localhost', port=9200, user='', password='', timeout=1000, index="test2", doc_type="tweet"):

        # Define config
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.index = index
        self.doc_type = doc_type
        self.size = 500
        self.body = {"query": {"match_all": {}}}
        self.result = []

        # Init Elasticsearch instance
        self.es = Elasticsearch(
            [self.host],
            http_auth=(self.user, self.password),
            port=self.port,
            timeout=self.timeout,
            use_ssl=False
        )

    # def search(self, query):
    #     res = self.es.search(
    #         index=self.index,
    #         doc_type=self.doc_type,
    #         body={"query": query},
    #         size=self.size,
    #     )
    #     if res['hits']['total']>0:
    #         print("Got %d Hits:" % res['hits']['total'])
    #     return res

    def search(self, query):
        res = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            body=query,
            size=self.size,
        )
        return res

    def count(self, query):
        res = self.es.count(
            index=self.index,
            doc_type=self.doc_type,
            body=query
        )
        return res

    def post(self, query):
        res = self.es.index(
            index=self.index,
            doc_type=self.doc_type,
            body=query
        )
        return res

    def update_field(self,id, field, value):
        res = self.es.update(
            index=self.index,
            doc_type=self.doc_type,
            id=id,
            body={"doc": {
                field: value
            }}
        )
        if res['result'] == "updated":
            return res
        else:
            return False

    def update(self,id, query):
        res = self.es.update(
            index=self.index,
            doc_type=self.doc_type,
            id=id,
            body=query
        )
        if res['result'] == "updated":
            return res
        else:
            return False

    def delete(self, id):
        res = self.es.delete(index=self.index,
            doc_type=self.doc_type,
            id=id)
        if res['result'] == "deleted":
            return res
        else:
            return False

    def get(self, id):
        res = self.es.get(index=self.index,
            doc_type=self.doc_type,
            id=id)
        if res['found'] == True:
            # print(res)
            return res
        else:
            return False


    def bigSearch(self, query):
        res = []
        # Process hits here
        def process_hits(hits, results):
            for item in hits:
                results.append(item)
            return results

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=query,
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        res = process_hits(data['hits']['hits'], res)

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            res = process_hits(data['hits']['hits'], res)

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        return res


    def init_paginatedSearch(self, query):
        res = []
        # Process hits here
        def process_hits(hits, results):
            for item in hits:
                results.append(item)
            return results

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=query,
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        res = process_hits(data['hits']['hits'], res)
        total = data['hits']['total']
        scroll_size = total - scroll_size

        return {"results":res, "sid":sid, "scroll_size":scroll_size, "total":total}


    def loop_paginatedSearch(self, sid, scroll_size):
        res = []
        # Process hits here
        def process_hits(hits, results):
            for item in hits:
                results.append(item)
            return results

        if scroll_size > 0:
            data = self.es.scroll(scroll_id=sid, scroll='15m')
            # Process current batch of hits
            res = process_hits(data['hits']['hits'], res)
            # Update the scroll ID
            sid = data['_scroll_id']
            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        return {"results": res, "sid": sid, "scroll_size": scroll_size}


    def getTweets(self):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                self.result.append(item)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        body = self.body
        body = {"_source": ["text", "timestamp_ms", "imagesCluster"],"query": {"match_all": {}}}

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        text = self.result[0]['_source']['text']
        date = self.result[0]['_source']['timestamp_ms']
        return self.result

    def getFilteredTweets(self, session, status):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                self.result.append(item)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        session ='session_'+session
        body = self.body
        body = {"_source": ["text", "timestamp_ms", "imagesCluster"],"query": {
            "terms": {
              session: status
            }
          }}

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        # text = self.result[0]['_source']['text']
        # date = self.result[0]['_source']['timestamp_ms']
        return self.result

    def update_all(self, field, value):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                self.update_field(item['_id'], field, value)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=self.body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        # print(data['hits']['total'])
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])
        return True

    def update_query(self, query, field, value):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                self.update_field(item['_id'], field, value)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=query
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        # print(data['hits']['total'])
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])
        return True

    def remove_field_all(self, field):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                item['_source'].pop(field, None)
                up = self.update(item['_id'], {"script" : "ctx._source.remove(\""+field+"\")"})
                # print(item['_id'])
                # print(up)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            return False

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=self.body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        # print(data['hits']['total'])
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])
        return True


    def initMABED(self):
        # Process hits here
        def process_hits(hits):
            for item in hits:
                self.result.append(item)

        # Check index exists
        if not self.es.indices.exists(index=self.index):
            # print("Index " + self.index + " not exists")
            exit()

        body = self.body
        body = {"_source": ["text", "timestamp_ms", "imagesCluster"], "query": {"match_all": {}}}

        # Init scroll by search
        data = self.es.search(
            index=self.index,
            doc_type=self.doc_type,
            scroll='15m',
            size=self.size,
            body=body
        )

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        # Before scroll, process current batch of hits
        process_hits(data['hits']['hits'])

        while scroll_size > 0:
            "Scrolling..."
            data = self.es.scroll(scroll_id=sid, scroll='15m')

            # Process current batch of hits
            process_hits(data['hits']['hits'])

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

        text = self.result[0]['_source']['text']
        date = self.result[0]['_source']['timestamp_ms']
        return self.result

