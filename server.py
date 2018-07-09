# coding: utf-8

import argparse
import json
# std
from datetime import datetime

# web
from flask import Flask, render_template, request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_frozen import Freezer
from flask import Response


# mabed
from mabed.functions import Functions

app = Flask(__name__, static_folder='browser/static', template_folder='browser/templates')



# ==================================================================
# 1. Tests and Debug
# ==================================================================

# Enable CORS
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Disable Cache
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


# Settings Form submit
@app.route('/settings', methods=['POST'])
@cross_origin()
def settings():
    data = request.form
    print(data)
    return jsonify(data)


@app.route('/event_descriptions')
def event_descriptions():
    event_descriptions = functions.event_descriptions("test3")
    events = []
    for event in event_descriptions:
        start_date = datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
        obj = {
            "media": {
                "url": "static/images/img.jpg"
            },
            "start_date": {
                "month": start_date.month,
                "day": start_date.day,
                "year": start_date.year
            },
            "end_date": {
                "month": end_date.month,
                "day": end_date.day,
                "year": end_date.year
            },
            "text": {
                "headline": event[3],
                "text": "<p>" + event[4] + "</p>"
            }
        }
        events.append(obj)
    res = {
        "events": events
    }
    return jsonify(res)

# ==================================================================
# 2. MABED
# ==================================================================

# Run MABED
@app.route('/detect_events', methods=['POST', 'GET'])
@cross_origin()
def detect_events():
    data = request.form
    print(data)
    index = data['index']
    k = int(data['top_events'])
    maf = float(data['min_absolute_frequency'])
    mrf = float(data['max_relative_frequency'])
    tsl = int(data['time_slice_length'])
    p = float(data['p_value'])
    theta = float(data['t_value'])
    sigma = float(data['s_value'])
    session = data['session']
    filter = data['filter']
    cluster = int(data['cluster'])
    events=""
    res = False
    if filter=="all":
        events = "all events"
        events = functions.event_descriptions(index, k, maf, mrf, tsl, p, theta, sigma, cluster)
    elif filter == "proposedconfirmed":
        filter = ["proposed","confirmed"]
        events = functions.filtered_event_descriptions(index, k, maf, mrf, tsl, p, theta, sigma, session, filter, cluster)
    else:
        events = functions.filtered_event_descriptions(index, k, maf, mrf, tsl, p, theta, sigma, session, [filter], cluster)

    if not events:
        events = "No Result!"
    else:
        res = True
    return jsonify({"result": res, "events":events})


# ==================================================================
# 3. Images
# ==================================================================

@app.route('/images')
def images():
    with open('twitter2015.json') as f:
        data = json.load(f)

    clusters_num = len(data['duplicates'])
    clusters = data['duplicates']
    return render_template('images.html',
                           clusters_num=clusters_num,
                           clusters=clusters
                           )

# ==================================================================
# 4. Tweets
# ==================================================================

# Get Tweets
@app.route('/tweets', methods=['POST'])
@cross_origin()
def tweets():
    data = request.form
    print(data['word'])
    print(data['index'])
    tweets= functions.get_tweets(index=data['index'], word=data['word'])
    clusters= functions.get_clusters(index=data['index'], word=data['word'])
    print(len(tweets))
    return jsonify({"tweets": tweets, "clusters": clusters})


# Get Event related tweets
@app.route('/event_tweets', methods=['POST'])
@cross_origin()
def event_tweets():
    data = request.form
    index = data['index']
    print(index)
    event = json.loads(data['obj'])
    main_term = event['main_term'].replace(",", " ")
    related_terms = event['related_terms']
    res = functions.get_event_tweets(index, main_term, related_terms)
    tweets = res['hits']['hits']
    clusters = functions.get_event_clusters(index, main_term, related_terms)
    print(clusters )
    return jsonify({"tweets": tweets, "clusters": clusters})


# Get Image Cluster tweets
@app.route('/cluster_tweets', methods=['POST', 'GET'])
@cross_origin()
def cluster_tweets():
    data = request.form
    index = data['index']
    cid = data['cid']
    event = json.loads(data['obj'])
    main_term = event['main_term'].replace(",", " ")
    related_terms = event['related_terms']
    # clusters = functions.get_event_clusters(index, main_term, related_terms)
    tres = functions.get_event_tweets2(index, main_term, related_terms, cid)
    event_tweets = tres
    # event_tweets = 0
    res = functions.get_cluster_tweets(index, cid)
    tweets = res['hits']['hits']
    return jsonify({"tweets": tweets, "event_tweets": event_tweets})

# Get Search Image Cluster tweets
@app.route('/cluster_search_tweets', methods=['POST', 'GET'])
@cross_origin()
def cluster_search_tweets():
    data = request.form
    index = data['index']
    cid = data['cid']
    word = data['word']
    search_tweets = functions.get_big_tweets(index=index, word=word)
    res = functions.get_cluster_tweets(index, cid)
    tweets = res['hits']['hits']
    return jsonify({"tweets": tweets, "search_tweets": search_tweets})

# Get Event main image
@app.route('/event_image', methods=['POST'])
@cross_origin()
def event_image():
    data = request.form
    index = data['index']
    print(index)
    event = json.loads(data['obj'])
    main_term = event['main_term'].replace(",", " ")
    related_terms = event['related_terms']
    image = functions.get_event_image(index, main_term, related_terms)
    res = False
    if image:
        image = image['hits']['hits'][0]['_source']
        res = True
    return jsonify({"result":res, "image": image})

# TODO mark as valid
# TODO mark as negative
# TODO mark as proposed
#   - All tweets (Testing & rest)
#   - Event related (inside Timeline)
#   - User (Tweet Option)
#   - Keyword (Search page)
#   - Cluster (Cluster card options)

# Test & Debug
@app.route('/mark_valid', methods=['POST', 'GET'])
@cross_origin()
def mark_valid():
    data = request.form
    print(data)
    res = functions.set_all_status("twitter2015", "session_Twitter2015", "proposed")
    return jsonify(res)



@app.route('/mark_event', methods=['POST', 'GET'])
@cross_origin()
def mark_event():
    data = request.form
    print(data)
    index = data['index']
    session = data['session']
    functions.set_status(index, session, data)
    return jsonify(data)

@app.route('/mark_cluster', methods=['POST', 'GET'])
@cross_origin()
def mark_cluster():
    data = request.form
    print(data)
    index = data['index']
    session = data['session']
    cid = data['cid']
    state = data['state']
    res = functions.set_cluster_state(index, session, cid, state)
    return jsonify(res)

@app.route('/mark_tweet', methods=['POST', 'GET'])
@cross_origin()
def mark_tweet():
    data = request.form
    print(data)
    index = data['index']
    session = data['session']
    tid = data['tid']
    val = data['val']
    functions.set_tweet_state(index, session, tid, val)
    return jsonify(data)


@app.route('/delete_field', methods=['POST', 'GET'])
@cross_origin()
def delete_field():
    up1 = functions.update_all("twitter2017", "tweet", "imagesCluster", "")
    # up = functions.delete_session("s1")
    # print(up)
    return jsonify(up1)

# ==================================================================
# 5. Export
# ==================================================================

@app.route('/export_events', methods=['POST', 'GET'])
@cross_origin()
def export_events():
    # data = request.form
    # session = data['session_id']
    # res = functions.get_session(session)
    res = functions.get_session('6n7aD2QBU2R9ngE9d8IB')
    index = res['_source']['s_index']
    events = json.loads(res['_source']['events'])
    for event in events:
        main_term = event['main_term'].replace(",", " ")
        # event['main_term']=main_term
        related_terms = event['related_terms']
        # tweets = functions.get_event_tweets(index, main_term, related_terms)
        # tweets = tweets['hits']['hits']
        event['tweets'] = 'tweets'

    return jsonify(events)
    # return Response(str(events),
    #     mimetype='application/json',
    #     headers={'Content-Disposition': 'attachment;filename=events.json'})

@app.route('/export_tweets', methods=['POST', 'GET'])
@cross_origin()
def export_tweets():
    # data = request.form
    # session = data['session_id']
    # res = functions.get_session(session)
    res = functions.get_session('6n7aD2QBU2R9ngE9d8IB')
    index = res['_source']['s_index']
    events = json.loads(res['_source']['events'])
    for event in events:
        main_term = event['main_term'].replace(",", " ")
        # event['main_term']=main_term
        related_terms = event['related_terms']
        # tweets = functions.get_event_tweets(index, main_term, related_terms)
        # tweets = tweets['hits']['hits']
        event['tweets'] = 'tweets'

    return jsonify(events)
    # return Response(str(events),
    #     mimetype='application/json',
    #     headers={'Content-Disposition': 'attachment;filename=events.json'})

# ==================================================================
# 6. Sessions
# ==================================================================

# Get Sessions
@app.route('/sessions', methods=['POST', 'GET'])
@cross_origin()
def sessions():
    data = request.form
    print(data)
    # up1 = functions.update_all("mabed_sessions", "session", "s_type", "tweet")
    # up = functions.delete_session("s1")
    # print(up)
    res = functions.get_sessions()
    return jsonify(res['hits']['hits'])

# Add new Session
@app.route('/add_session', methods=['POST'])
@cross_origin()
def add_session():
    data = request.form
    name = data['s_name']
    index = data['s_index']
    res = functions.add_session(name, index)
    print(res)
    status = False
    if res:
        status = True
    return jsonify({"result": status, "body": res})


# Delete Session
@app.route('/delete_session', methods=['POST'])
@cross_origin()
def delete_session():
    data = request.form
    id = data['id']
    print(id)
    res = functions.delete_session(id)
    return jsonify({"result": res})


# Get Session
@app.route('/get_session', methods=['POST'])
@cross_origin()
def get_session():
    data = request.form
    id = data['id']
    print(id)
    res = functions.get_session(id)
    status = False
    if res:
        status = True
    return jsonify({"result": status, "body": res})


# Update session results
@app.route('/update_session_results', methods=['POST'])
@cross_origin()
def update_session_results():
    data = request.form
    events = data['events']
    impact_data = data['impact_data']
    index = data['index']
    res = functions.update_session_results(index, events, impact_data)
    print(res)
    status = False
    if res:
        status = True
    return jsonify({"result": status, "body": res})


# Get session results
@app.route('/get_session_results', methods=['POST', 'GET'])
@cross_origin()
def get_session_results():
    data = request.form
    index = data['index']
    res = functions.get_session_results(index)
    print(res)
    status = False
    if res:
        status = True
    return jsonify({"result": status, "body": res})


# ==================================================================
# 6. Main
# ==================================================================
@app.route('/')
def ind():
    return render_template('index.html')


if __name__ == '__main__':
    functions = Functions()
    app.run(debug=True, host='localhost', port=2016)
