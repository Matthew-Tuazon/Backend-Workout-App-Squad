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
#client = MongoClient('')
workout_db = client['workout-db']

def check_credentials(username, password):
    users_coll = workout_db['users']
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

#creates a user, assigns unique ID during mongodb creation
@app.route("/users", methods=["POST"])
def users():
    if request.method == 'POST':
        body = request.get_json()
        users = workout_db['users']
        user = {
            "username": body["username"]
        }
        users.insert_one(user)
        return "User: " + user["username"] + " was added."

#returns what User, passes in userid in route
@app.route("/users/<userid>", methods=["GET"])
def get_users(userid):
    if request.method == 'GET':
        users_coll = workout_db['users']
        return Response(JSONEncoder().encode(users_coll.find_one({"_id": ObjectId(userid)})), mimetype='application/json')

#POSTS's an exercise by passing in JSON body
#GET's exercise when passing in exercise name in JSON body
#DELETE's exercise when passing in exercise name in JSON body.
#TODO: ???
@app.route("/exercises", methods=["POST", "GET","DELETE"])
def exercises():
    if request.method == 'GET':
        exercises_coll = workout_db['exercises']
        return Response(JSONEncoder().encode(list(exercises_coll.find())), mimetype='application/json')
    elif request.method == 'POST':
        body = request.get_json()
        exercises = workout_db['exercises']
        exercise = {
            "sets": {
                "reps": body["sets"]["reps"],
                "weights": body["sets"]["weights"]
                },
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


@app.route("/logs/<date>", methods=["GET"])
def single_date(date):
    logs = workout_db['logs']
    return Response(JSONEncoder().encode(list(logs_coll.find())), mimetype='application/json')

#TODO: ask, would final route be /users/<userid>/logs/<date/logsid>/exercises
#or would it just simply be the user is logged in so it's just: /logs/<date/logsid>/exercises


if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0', port=port)