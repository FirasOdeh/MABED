# coding: utf-8

import timeit
import json
import time

from flask import jsonify
from mabed.es_corpus import Corpus
from mabed.mabed import MABED
from mabed.es_connector import Es_connector

__author__ = "Firas Odeh"
__email__ = "odehfiras@gmail.com"

# Interface Functions
class Functions:
    def __init__(self):
        self.sessions_index = 'mabed_sessions'
        self.sessions_doc_type = 'session'
        # print("Functions init")

    # ==================================================================
    # Event Detection
    # ==================================================================

    def detect_events(self, index="test3", k=10, maf=10, mrf=0.4, tsl=30, p=10, theta=0.6, sigma=0.6, cluster=2):
        sw = 'stopwords/twitter_all.txt'
        sep = '\t'
        print('Parameters:')
        print(
            '   Index: %s\n   k: %d\n   Stop-words: %s\n   Min. abs. word frequency: %d\n   Max. rel. word frequency: %f' %
            (index, k, sw, maf, mrf))
        print('   p: %d\n   theta: %f\n   sigma: %f' % (p, theta, sigma))

        print('Loading corpus...')
        start_time = timeit.default_timer()
        my_corpus = Corpus(sw, maf, mrf, sep, index=index)
        elapsed = timeit.default_timer() - start_time
        print('Corpus loaded in %f seconds.' % elapsed)

        time_slice_length = tsl
        print('Partitioning tweets into %d-minute time-slices...' % time_slice_length)
        start_time = timeit.default_timer()
        my_corpus.discretize(time_slice_length, cluster)
        elapsed = timeit.default_timer() - start_time
        print('Partitioning done in %f seconds.' % elapsed)

        print('Running MABED...')
        start_time = timeit.default_timer()
        mabed = MABED(my_corpus)
        mabed.run(k=k, p=p, theta=theta, sigma=sigma)
        elapsed = timeit.default_timer() - start_time
        print('Event detection performed in %f seconds.' % elapsed)
        return mabed


    def event_descriptions(self, index="test3", k=10, maf=10, mrf=0.4, tsl=30, p=10, theta=0.6, sigma=0.6, cluster=2):
        mabed = self.detect_events(index, k, maf, mrf, tsl, p, theta, sigma, cluster)

        # format data
        event_descriptions = []
        impact_data = []
        formatted_dates = []
        for i in range(0, mabed.corpus.time_slice_count):
            formatted_dates.append(int(time.mktime(mabed.corpus.to_date(i).timetuple())) * 1000)

        for event in mabed.events:
            mag = event[0]
            main_term = event[2]
            raw_anomaly = event[4]
            formatted_anomaly = []
            time_interval = event[1]
            related_terms = []
            for related_term in event[3]:
                # related_terms.append(related_term[0] + ' (' + str("{0:.2f}".format(related_term[1])) + ')')
                related_terms.append({'word':related_term[0], 'value':str("{0:.2f}".format(related_term[1])) })
            event_descriptions.append((mag,
                                       str(mabed.corpus.to_date(time_interval[0])),
                                       str(mabed.corpus.to_date(time_interval[1])),
                                       main_term,
                                       json.dumps(related_terms)))
            for i in range(0, mabed.corpus.time_slice_count):
                value = 0
                if time_interval[0] <= i <= time_interval[1]:
                    value = raw_anomaly[i]
                    if value < 0:
                        value = 0
                formatted_anomaly.append([ formatted_dates[i],value])
            impact_data.append({"key": main_term, "values": formatted_anomaly})

        return {"event_descriptions": event_descriptions, "impact_data": impact_data}


    def detect_filtered_events(self, index="test3", k=10, maf=10, mrf=0.4, tsl=30, p=10, theta=0.6, sigma=0.6, session=False, filter=False, cluster=2):
        sw = 'stopwords/twitter_all.txt'
        sep = '\t'
        print('Parameters:')
        print(
            '   Index: %s\n   k: %d\n   Stop-words: %s\n   Min. abs. word frequency: %d\n   Max. rel. word frequency: %f' %
            (index, k, sw, maf, mrf))
        print('   p: %d\n   theta: %f\n   sigma: %f' % (p, theta, sigma))

        print('Loading corpus...')
        start_time = timeit.default_timer()
        my_corpus = Corpus(sw, maf, mrf, sep, index=index, session=session, filter=filter)
        if not my_corpus.tweets:
            return False

        elapsed = timeit.default_timer() - start_time
        print('Corpus loaded in %f seconds.' % elapsed)

        time_slice_length = tsl
        print('Partitioning tweets into %d-minute time-slices...' % time_slice_length)
        start_time = timeit.default_timer()
        my_corpus.discretize(time_slice_length, cluster)
        elapsed = timeit.default_timer() - start_time
        print('Partitioning done in %f seconds.' % elapsed)

        print('Running MABED...')
        start_time = timeit.default_timer()
        mabed = MABED(my_corpus)
        mabed.run(k=k, p=p, theta=theta, sigma=sigma)
        elapsed = timeit.default_timer() - start_time
        print('Event detection performed in %f seconds.' % elapsed)
        return mabed

    def filtered_event_descriptions(self, index="test3", k=10, maf=10, mrf=0.4, tsl=30, p=10, theta=0.6, sigma=0.6, session=False, filter=False, cluster=2):
        mabed = self.detect_filtered_events(index, k, maf, mrf, tsl, p, theta, sigma, session, filter, cluster)
        if not mabed:
            return False

        # format data
        event_descriptions = []
        impact_data = []
        formatted_dates = []
        for i in range(0, mabed.corpus.time_slice_count):
            formatted_dates.append(int(time.mktime(mabed.corpus.to_date(i).timetuple())) * 1000)

        for event in mabed.events:
            mag = event[0]
            main_term = event[2]
            raw_anomaly = event[4]
            formatted_anomaly = []
            time_interval = event[1]
            related_terms = []
            for related_term in event[3]:
                # related_terms.append(related_term[0] + ' (' + str("{0:.2f}".format(related_term[1])) + ')')
                related_terms.append({'word':related_term[0], 'value':str("{0:.2f}".format(related_term[1])) })
            event_descriptions.append((mag,
                                       str(mabed.corpus.to_date(time_interval[0])),
                                       str(mabed.corpus.to_date(time_interval[1])),
                                       main_term,
                                       json.dumps(related_terms)))
            for i in range(0, mabed.corpus.time_slice_count):
                value = 0
                if time_interval[0] <= i <= time_interval[1]:
                    value = raw_anomaly[i]
                    if value < 0:
                        value = 0
                formatted_anomaly.append([ formatted_dates[i],value])
            impact_data.append({"key": main_term, "values": formatted_anomaly})

        return {"event_descriptions": event_descriptions, "impact_data": impact_data}

    # ==================================================================
    # Tweets
    # ==================================================================

    def get_tweets(self, index="test3", word=""):
        my_connector = Es_connector(index=index)
        # res = my_connector.search({
        #         "query": {
        #             "simple_query_string": {
        #               "fields": [
        #                 "text"
        #               ],
        #               "query": word
        #             }
        #           }
        #         })

        # res = my_connector.bigSearch(
        #     {
        #         "_source": ["text", "id_str", "extended_entities", "user", "created_at", "link"],
        #         "query": {
        #             "simple_query_string": {
        #               "fields": [
        #                 "text"
        #               ],
        #               "query": word
        #             }
        #           }
        #     })

        res = my_connector.init_paginatedSearch({
            "query": {
                "simple_query_string": {
                    "fields": [
                        "text"
                    ],
                    "query": word
                }
            }
        })
        return res


    def get_tweets_scroll(self, index, sid, scroll_size):
        my_connector = Es_connector(index=index)
        res = my_connector.loop_paginatedSearch(sid, scroll_size)
        return res

    def get_big_tweets(self, index="test3", word=""):
        my_connector = Es_connector(index=index)
        res = my_connector.bigSearch(
            {
                "_source": ["text", "id_str", "extended_entities", "user", "created_at", "link"],
                "query": {
                    "simple_query_string": {
                      "fields": [
                        "text"
                      ],
                      "query": word
                    }
                  }
            })
        return res


    def get_tweets_state(self, index="test3", session="",state="proposed"):
        my_connector = Es_connector(index=index)
        res = my_connector.init_paginatedSearch(
            {
                "query": {
                    "term": {
                        "session_"+session: state
                    }
                }
            })
        return res

    def get_big_tweets_scroll(self, index="test3", word=""):
        my_connector = Es_connector(index=index)
        res = my_connector.init_paginatedSearch(
            {
                "_source": ["text", "id_str", "extended_entities", "user", "created_at", "link"],
                "query": {
                    "simple_query_string": {
                      "fields": [
                        "text"
                      ],
                      "query": word
                    }
                  }
            })
        return res


    def get_event_tweets(self, index="test3", main_term="", related_terms=""):
        my_connector = Es_connector(index=index)
        terms = []
        words = main_term + ' '
        for t in related_terms:
            terms.append({ "match": {
                    "text": {
                        "query": t['word'],
                        "boost": t['value']
                    }
                }})
            words += t['word']+ " "
        terms.append({"match": {
            "text": {
                "query": main_term,
                "boost": 2
            }
        }})
        # res = my_connector.search({"query": {"term" : { "text" : word }}})
        # query = {
        #     "bool": {
        #         "must": {
        #             "match": {
        #                 "text": {
        #                     "query": main_term,
        #                     "operator": "or"
        #                 }
        #             }
        #         },
        #         "should": terms
        #     }
        # }
        query = {
            "sort": [
                "_score"
            ],
                "query": {
                        "bool": {
                            "should": terms
                        }
                    }
                }
        # print(query)
        # res = my_connector.search(query)
        res = my_connector.init_paginatedSearch(query)
        return res


    def get_event_tweets2(self, index="test3", main_term="", related_terms="", cid =0):
        my_connector = Es_connector(index=index)
        terms = []
        words = main_term + ' '
        for t in related_terms:
            terms.append({ "match": {
                    "text": {
                        "query": t['word'],
                        "boost": t['value']
                    }
                }})
            words += t['word']+ " "
        terms.append({"match": {
            "text": {
                "query": main_term,
                "boost": 2
            }
        }})
        # terms.append({"match": {
        #     "imagesCluster": {
        #         "query": cid
        #     }
        # }})
        # query = {
        #         "query": {
        #                 "bool": {
        #                     "must": {
        #                         "exists": {
        #                             "field": "imagesCluster"
        #                         }
        #                     },
        #                     # "must": { "match": { "imagesCluster" : cid }},
        #                     "should": terms
        #                 }
        #             }
        #         }

        query = {
            "sort": [
                "_score"
            ],
            "query": {
                "bool": {
                    "should": terms,
                    "minimum_should_match": 1,
                    "must": [
                        {
                            "match": {
                                "imagesCluster": cid
                            }
                        }
                    ]
                }
            }
        }

        # res = my_connector.bigSearch(query)
        res = my_connector.init_paginatedSearch(query)
        return res

    def get_cluster_tweets(self, index="test3", cid=0):
        my_connector = Es_connector(index=index)
        query = {
                # "_source": [
                #     "id_str",
                #     "imagesCluster",
                #     "session_Twitter2015",
                #     "extended_entities"
                # ],
                "query": {
                        "term" : { "imagesCluster": cid }
                    }
                }
        res = my_connector.search(query)
        return res


    def get_event_image(self, index="test3", main_term="", related_terms=""):
        my_connector = Es_connector(index=index)
        terms = []
        words = main_term + ' '
        for t in related_terms:
            terms.append({ "match": {
                    "text": {
                        "query": t['word'],
                        "boost": t['value']
                    }
                }})
            words += t['word']+ " "
        terms.append({"match": {
            "text": {
                "query": main_term,
                "boost": 2
            }
        }})
        # res = my_connector.search({"query": {"term" : { "text" : word }}})
        # query = {
        #     "bool": {
        #         "must": {
        #             "match": {
        #                 "text": {
        #                     "query": main_term,
        #                     "operator": "or"
        #                 }
        #             }
        #         },
        #         "should": terms
        #     }
        # }
        query = {
                "size": 1,
                "_source": [
                    "id_str",
                    "imagesCluster",
                    "session_Twitter2015",
                    "extended_entities"
                ],
                "query": {
                        "bool": {
                            "must":
                                    {
                                        "exists": {
                                            "field": "extended_entities"
                                        }
                                    },
                            "should": terms
                        }
                    }
                }
        # print(query)
        res = my_connector.search(query)
        return res

    def get_valid_tweets(self, index="test3"):
        my_connector = Es_connector(index=index)
        res = my_connector.search({
                "query": {
                    "simple_query_string": {
                      "fields": [
                        "text"
                      ],
                      "query": word
                    }
                  }
                })
        # res = my_connector.bigSearch(
        #     {
        #         "_source": ["text", "id_str", "extended_entities", "user", "created_at", "link"],
        #         "query": {
        #             "simple_query_string": {
        #               "fields": [
        #                 "text"
        #               ],
        #               "query": word
        #             }
        #           }
        #     })
        return res['hits']['hits']


    # ==================================================================
    # Clusters
    # ==================================================================

    def get_clusters(self, index="test3", word=""):
        my_connector = Es_connector(index=index)
        res = my_connector.search({
          "size": 1,
          "query": {
            "simple_query_string": {
              "fields": [
                "text"
              ],
              "query": word
            }
          },
          "aggs": {
            "group_by_cluster": {
              "terms": {
                "field": "imagesCluster",
                "size": 9999
              }
            }
          }
        })
        # print("Clusters")
        # print(res['aggregations']['group_by_cluster']['buckets'])
        clusters = res['aggregations']['group_by_cluster']['buckets']
        with open(index+'.json') as f:
            data = json.load(f)
        for cluster in clusters:
            # print(cluster['key'])
            images = data['duplicates'][cluster['key']]
            # print(images[0])
            cluster['image']=images[0]
            cluster['size'] = len(images)
        # print(clusters)
        return clusters

    def get_event_clusters(self, index="test3", main_term="", related_terms=""):
        my_connector = Es_connector(index=index)
        terms = []
        words = main_term + ' '
        for t in related_terms:
            terms.append({ "match": {
                    "text": {
                        "query": t['word'],
                        "boost": t['value']
                    }
                }})
            words += t['word']+ " "
        terms.append({"match": {
            "text": {
                "query": main_term,
                "boost": 2
            }
        }})
        # query = {
        #     "size": 0,
        #     "query": {
        #             "bool": {
        #                 "should": terms
        #             }
        #         },
        #     "aggs": {
        #         "group_by_cluster": {
        #             "terms": {
        #                 "field": "imagesCluster",
        #                 "size": 200
        #             }
        #         }
        #     }
        # }
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "should": terms
                }
            },
            "aggregations": {
                "group_by_cluster": {
                    "terms": {
                        "field": "imagesCluster",
                        # "shard_size": 999999999,
                        "size": 999999
                    }
                }
            }
        }
        print(query)
        res = my_connector.search(query)
        print("Clusters")
        # print(res['aggregations']['group_by_cluster']['buckets'])
        clusters = res['aggregations']['group_by_cluster']['buckets']
        with open(index + '.json') as f:
            data = json.load(f)


        for cluster in clusters:
            # q1 = {
            #       "_source": [
            #         "text",
            #         "imagesCluster"
            #       ],
            #       "query": {
            #         "bool": {
            #            "should": terms,
            #           "filter": {
            #             "bool": {
            #               "should": [
            #                 {
            #                   "match": {
            #                     "imagesCluster": cluster['key']
            #                   }
            #                 }
            #               ]
            #             }
            #           }
            #         }
            #       }
            #     }
            q2 = {
                "query": {
                    "term": {"imagesCluster": cluster['key']}
                }
            }
            # cres1 = my_connector.search(q1)
            cres = my_connector.count(q2)
            print(cluster['key'])
            images = data['duplicates'][cluster['key']]
            print(images[0])
            cluster['image'] = images[0]
            # cluster['size'] = len(images)
            # print(cres)
            cluster['size'] = cres['count']
            # cluster['size2'] = cres1['hits']['total']
            # if cluster['key']==1452:
            #     print(cluster)
        print(clusters)
        return clusters

    # ==================================================================
    # Sessions
    # ==================================================================

    # Get all sessions
    def get_sessions(self):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        query = {
                "query":  {
                    "match_all": {}
                  }
                }

        res = my_connector.search(query)
        return res

    # Get session by session ID
    def get_session(self, id):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        print("firas")
        res = my_connector.get(id)
        return res

    # Get session by session name
    def get_session_by_Name(self, name):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        query = {
                "query": {
                        "constant_score" : {
                            "filter" : {
                                "term" : {
                                    "s_name" : name
                                }
                            }
                        }
                    }
                }
        res = my_connector.search(query)
        return res


    # Add new session
    def add_session(self, name, index):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        session = self.get_session_by_Name(name)
        if session['hits']['total']==0:
            res = my_connector.post({
              "s_name": name,
              "s_index": index,
              "s_type": "tweet"
            })
            tweets_connector = Es_connector(index=index, doc_type="tweet")
            tweets_connector.update_all('session_'+name, 'proposed')
            return res
        else:
            return False


    # Update specific field value in an Index
    def update_all(self, index, doc_type, field, value):
        my_connector = Es_connector(index=index, doc_type=doc_type)
        res = my_connector.update_all(field, value)
        return res

    # Update session events results
    def update_session_results(self, id, events, impact_data):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        res = my_connector.update(id, {
            "doc" : {
                "events" : events,
                "impact_data": impact_data
            }
        })
        return res

    # Get session events results
    def get_session_results(self, id):
        my_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        res = my_connector.get(id)
        return res


    # Delete session by name
    def delete_session(self, id):
        session_connector = Es_connector(index=self.sessions_index, doc_type=self.sessions_doc_type)
        session = session_connector.get(id)
        if session:
            print("Session:")
            # print(session)
            # 1. Delete session data from the tweets
            tweets_connector = Es_connector(index=session['_source']['s_index'], doc_type=session['_source']['s_type'])
            session_name = 'session_'+session['_source']['s_name']
            print(session_name)
            tweets_connector.remove_field_all(session_name)
            # 2. Delete the session
            session_connector.delete(id)
            return True
        else:
            return False

    # ==================================================================
    # Tweets session status
    # ==================================================================

    # Set tweets status
    def set_all_status(self, index, session, status):
        tweets_connector = Es_connector(index=index, doc_type="tweet")
        res = tweets_connector.update_all(session, status)
        return res

    def set_status(self, index, session, data):
        tweets_connector = Es_connector(index=index, doc_type="tweet")
        # All tweets
        session = 'session_'+session
        event = json.loads(data['event'])
        print("------------------------")
        print(data)
        print("------------------------")
        print(event)
        print(event['main_term'])
        terms = []
        words = event['main_term'] + ' '
        for t in event['related_terms']:
            terms.append({"match": {
                "text": {
                    "query": t['word'],
                    "boost": t['value']
                }
            }})
            words += t['word'] + " "
        terms.append({"match": {
            "text": {
                "query": event['main_term'],
                "boost": 2
            }
        }})
        query = {
            "query": {
                "bool": {
                    "should": terms
                }
            }
        }

        # print(query)
        res = tweets_connector.update_query(query, session, data['status'])
        # Event related

        return res

    def set_cluster_state(self, index, session, cid, state):
        tweets_connector = Es_connector(index=index, doc_type="tweet")
        # All tweets
        session = 'session_'+session
        query = {
                "query": {
                        "term" : { "imagesCluster": cid }
                    }
                }
        res = tweets_connector.update_query(query, session, state)
        return res

    def set_tweet_state(self, index, session, tid, val):
        tweets_connector = Es_connector(index=index, doc_type="tweet")
        session = 'session_'+session

        query = {
            "doc" : {
                session : val
            }
        }
        res = tweets_connector.update(tid, query)
        return res


    def export_event(self, index, session):
        my_connector = Es_connector(index=index)
        res = my_connector.bigSearch(
            {
                "_source": {
                    "excludes": ["session_*"]
                },
                "query": {
                    "term": {
                        "session_"+session: "confirmed"
                    }
                }
            })
        return res