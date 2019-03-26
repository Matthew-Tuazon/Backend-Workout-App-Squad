from flask import Flask, request, jsonify, Response
from functools import wraps
import json
from pymongo import MongoClient
from bson import ObjectId
import datetime
app = Flask(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

client = MongoClient('localhost', 27017)

workout_db = client['workout-db']

def check_credentials(username, password):
    users_coll = blog_db['users']
    user = users_coll.find_one({"username": username})
    if user is None:
        return False
    if user['password'] != password:
        return False
    return True

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Auth')
        if auth is None:
            return "invalid"
        tokens = auth.split(':')
        if len(tokens) != 2:
            return "invalid"
        if not auth or not check_credentials(tokens[0], tokens[1]):
            return "invalid"
        return f(*args, **kwargs)
    return decorated

@app.route("/exercises", methods=["POST", "GET","DELETE"])
def exercises():
    if request.method == 'GET':
        exercises_coll = workout_db['exercises']
        return Response(JSONEncoder().encode(list(exercises_coll.find())), mimetype='application/json')
    elif request.method == 'POST':
        body = request.get_json()
        exercises = workout_db['exercises']
        exercise = {
            #"sets": [body["reps"], body["weights"]],
            "name": body["name"],
            "templateID": body["templateID"],
            "created": str(datetime.datetime.now())
        }
        exercises.insert_one(exercise)
        return "Done."
    else:
        body = request.get_json()
        exercises = workout_db['exercises']
        deleteExercise = {
            "name": body["name"]
        }
        exercises.delete_one(deleteExercise)
        return "Deleted " + body["name"] + "."