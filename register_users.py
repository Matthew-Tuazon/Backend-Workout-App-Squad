from flask import Flask, request, jsonify
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
        return json.JSONEncoder.default(self,o)


client = MongoClient