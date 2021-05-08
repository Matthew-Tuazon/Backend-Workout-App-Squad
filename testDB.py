from flask import Flask, request, jsonify, Response
from functools import wraps
import json
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import loads, dumps
import datetime
import os
import random

app = Flask(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#make changes to local database, uncomment when testing locally
client = MongoClient('localhost', 27017)

#makes changes to actual database, uncomment when using Heroku
# client = MongoClient('mongodb://MattTuazon:' + os.environ.get('ATLAS_PASSWORD') + '@workoutappsquad-shard-00-00-l4tr0.mongodb.net:27017,workoutappsquad-shard-00-01-l4tr0.mongodb.net:27017,workoutappsquad-shard-00-02-l4tr0.mongodb.net:27017/test?ssl=true&replicaSet=WorkoutAppSquad-shard-0&authSource=admin&retryWrites=true')

workout_db = client['workout-db']

#TODO: auth has no functionality for now, will fix this later.
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

@app.route("/")
def hello():
    List = ["Honeydew", "Taro", "Thai", "Coconut",
    "Coffee", "Chocolate", "Mango", "Passion Fruit", 
    "Strawberry", "Matcha", "Lychee", "Pineapple", "Taro + Green Tea",
    "Mango + Lychee", "Pineapple + Lychee", "Chocolate + Peanut", "Strawberry + Banana", 
    "Taro + Coconut", "Blueberry + Strawberry"
    ]   

    return random.choice(List) + " Bubble Tea"



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

#POST's an exercise by passing in JSON body
#GET's exercise when passing in exercise name in JSON body
#DELETE's exercise when passing in exercise name in JSON body.
#TODO: ???

@app.route("/exercises", methods=["POST", "GET", "DELETE"])
def exercises():
    if request.method == 'GET':
        exercises_coll = workout_db['exercises']
        #print(dumps((exercises_coll.find({}))))
        return Response(JSONEncoder().encode(list(exercises_coll.find())), mimetype='application/json')
    elif request.method == 'POST':
        body = request.get_json()
        exercises = workout_db['exercises']

        exercise = {
            "sets": body["sets"],
            "name": body["name"],
            #for now, templateID == name
            "templateID": body["name"],
            "created": str(datetime.datetime.now())
        }

        exercises.insert_one(exercise)
        return "Done."

    #if request method was DELETE (changed to POST route since Android had complications)
    
    elif request.method == 'DELETE':
        body = request.get_json()
        exercises = workout_db['exercises']
        deleteExercise = {
            "name": body["name"]
        }
        exercises.delete_one(deleteExercise)
        return "Deleted " + body["name"] + "."
    
    
#if wanted to make POST/GET exercise routes specific to users
'''
#POST's exercise to specific user
#GET's exercise for specific user
@app.route("/users/<userid>/exercises", methods=["POST", "GET"])
def exercises(userid):
    if request.method == 'GET':
        exercises_coll = workout_db['exercises']
        #print(dumps((exercises_coll.find({}))))
        #return Response(JSONEncoder().encode(list(logs_coll.find({"_userid": userid, "_date": date}))), mimetype='application/json')
        return Response(JSONEncoder().encode(list(exercises_coll.find({"_exercise.userid": body[""]}))), mimetype='application/json')
    elif request.method == 'POST':
        body = request.get_json()
        exercises = workout_db['exercises']

        exercise = {
            "sets": body["sets"],
            "name": body["name"],
            #for now, templateID == name
            "templateID": body["name"],
            "userid": userid,
            "created": str(datetime.datetime.now())
        }

        exercises.insert_one(exercise)
        return "Done."

#TODO: plan out template route
#GET's all templates made
#POST's creates template
@app.route("/templates", methods=["GET", "POST"])
def templates():
    if request.method == 'GET':
        templates_coll = workout_db['templates']
        return Response(JSONEncoder().encode(list(templates_coll.find())), mimetype='application/json')
    elif request.method == 'POST':
        body = request.get_json()
        templates = workout_db['templates']
        template = {

        }

'''


#POST specific exercise for a specific user log: provides date, userid, and exercise object
@app.route("/users/<userid>/logs/<exercise>", methods=["POST"])
def post_logs(userid, exercise):
    if request.method == 'POST':
        users_coll = workout_db['users']
        exercises_coll = workout_db['exercises']

        #returns json format of exercise, this way we can get unique id for exercise
        exercise_json = (exercises_coll.find_one({"name": (exercise)}))
        exercise_id = exercise_json["_id"]

        user_id = users_coll.find_one({"_id": ObjectId(userid)})
        exercise_object = exercises_coll.find_one({"_id": ObjectId(exercise_id)})

        if user_id is None:
            return "userid: " + userid + " is not in database."
        if exercise_object is None:
            return "exercise: " + exercise_object + " is not in database."
        
        #if user_id/exercise_object is in database, continue
        body = request.get_json()
        logs = workout_db['logs']
        log = {
            "_date": body["date"],
            "_userid": userid,
            "_exercise": exercise_object
        }
        logs.insert_one(log)
        return "Done. User is: " + userid + ". Log was added for date: " + log["_date"] + "."


#GET Returns logs for specific user for a specific date
@app.route("/users/<userid>/logs/<date>", methods=["GET"])
def get_logs(userid, date):
    if request.method == 'GET':
        #users_coll = workout_db['users']
        logs_coll = workout_db['logs']

        #finds userid using unique _id and matches with userid passed in route
        #finds matching log date using date and matches with date passed in route
        return Response(JSONEncoder().encode(list(logs_coll.find({"_userid": userid, "_date": date}))), mimetype='application/json')

#POST is technically a DELETE route, but Android has problems with DELETE. 
#deletes exercise for specific user at specific log date, takes in "id" as body, which is the ObjectId.
#i know route naming sux, not sure what do for now
@app.route("/users/<userid>/logs/<date>/delete_exercise", methods=["POST"])
def delete_exercise(userid, date):
    if request.method == 'POST':
        body = request.get_json()
        logs_coll = workout_db['logs']
        exercise_json = logs_coll.find_one({"_userid": userid, "_date": date, "_id": ObjectId(body["_id"])})
        
        #makes for pretty response message
        exercise_name = exercise_json['_exercise']['name']
        logs_coll.remove({"_userid": userid, "_date": date, "_id": ObjectId(body["_id"])})
        return "Deleted " + exercise_name  + "."

#TODO: ask, would final route be /users/<userid>/logs/<date/logsid>/exercises
#or would it just simply be the user is logged in so it's just: /logs/<date/logsid>/exercises


if __name__ == "__main__":
    app.run()
    #port = int(os.environ.get("PORT",5000))
   # app.run(host='0.0.0.0', port=port)