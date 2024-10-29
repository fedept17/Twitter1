import neca
from neca.events import *
from neca.generators import generate_data
from flask import Flask, jsonify
from neca.settings import app, socket


tweets = create_context("tweets")

@event("init")
def init(context, data):
	generate_data('./p2000.txt', time_scale=100, event_name='tweet', limit=100) 

@event("tweet")
def my_event_handler(context, data):
    emit("new_tweet", data)
    tweets[1] = data

@app.route("/data")
def get_data():
   # Return the actual tweets data
	return jsonify(tweets[1])

# starts the server
neca.start()
