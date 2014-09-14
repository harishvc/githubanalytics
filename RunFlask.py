#Source: https://github.com/mganache/helloapp/
#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from flask import Flask
from flask import render_template
from datetime import datetime, timedelta
import json
import os.path, time
import operator
from pymongo import MongoClient
from jinja2 import Template
import HTMLParser
from json import loads

#Configure for production or development based on environment variables
if (os.environ['deployEnv'] == "production"):
    MONGO_URL = os.environ['connectURL']
    connection = MongoClient(MONGO_URL)
    db = connection.githublive.pushevent
else: 
    MONGO_URL = os.environ['connectURLdev']
    connection = MongoClient(MONGO_URL)
    db = connection.githubdev.pushevent
    

#Global variables
LimitActiveLanguages=5
LimitActiveLanguagesBubble=10
LimitActiveRepositories=5
LimitActiveUsers=5


def TotalEntries ():
    return db.count()

def FindOneTimeStamp(type):
    pipeline= [
           { '$match': {} }, 
           { '$project': { '_id': 0, 'created_at': '$created_at'}},
           { '$sort' : { 'created_at': type }},
           { '$limit': 1}
           ]
    mycursor = db.aggregate(pipeline)
    for record in mycursor["result"]:
        return (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record["created_at"]/1000)))

def ActiveLanguages ():
    pipeline= [
           { '$match': {'$and': [{"language":{"$ne":"null"}},{"language":{"$ne":None}}] }},  
           { '$group': {'_id': {'language': '$language'}, 'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'language': '$_id.language', 'count': '$count' } },
           { '$sort' : { 'count': -1 }},
           { '$limit': LimitActiveLanguages}
           ]
    mycursor = db.aggregate(pipeline)
    return mycursor

def ActiveLanguagesBubble ():
    a1 =[]
    pipeline= [
           { '$match': {'$and': [{"language":{"$ne":"null"}},{"language":{"$ne":None}}] }},  
           { '$group': {'_id': {'language': '$language'}, 'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'language': '$_id.language', 'count': '$count' } },
           { '$sort' : { 'count': -1 }},
           { '$limit': LimitActiveLanguagesBubble}
           ]
    mycursor = db.aggregate(pipeline);
    #convert cursor to array
    for record in mycursor["result"]:
           #remove unicode
           t1 = "{:,}".format(record["count"])
           #size2 is formatted
           a1.append({"name":str(record["language"]), "size":str(record["count"]),"size2":str(t1)});  
    #create custom dictionary
    return ({"name": "something", "children": a1})


def ActiveRepositories ():
    pipeline= [
           { '$match': {}}, 
           { '$group': {'_id': {'url': '$url',  'name': "$name", 'language': "$language"}, 'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'count': '$count',  'name': "$_id.name", 'language': "$_id.language" } },
           { '$sort' : { 'count': -1 }},
           { '$limit': LimitActiveRepositories}
           ]
    mycursor = db.aggregate(pipeline)
    #print "#############" , mycursor['result']
    return mycursor

def ActiveUsers ():
    pipeline= [
           { '$match': {}}, 
           { '$group': {'_id': {'actorlogin': '$actorlogin',  'actorname': "$actorname"}, 'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'actorname': '$_id.actorname', 'count': '$count',  'actorlogin': "$_id.actorlogin"} },
           { '$sort' : { 'count': -1 }},
           { '$limit': LimitActiveUsers}
           ]
    mycursor = db.aggregate(pipeline)
    return mycursor

def CloseDB():
    connection.close()


#TODO
#http://stackoverflow.com/questions/850795/clearing-python-lists    
#def refresh_data():

app = Flask(__name__)

#Format integers with comma
@app.template_filter()
def numformat(value):
    return "{:,}".format(value)
app.jinja_env.filters['numformat'] = numformat
   
@app.route('/')
@app.route('/index')
def index():
    #refresh_data()
    return render_template("index.html",
        title = 'GitHub Analytics',
	    LCA = ActiveLanguagesBubble(),
        AR = ActiveRepositories(),
        AU = ActiveUsers(),
        total = TotalEntries(),
        start = FindOneTimeStamp(1),
        end = FindOneTimeStamp(-1)
	)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.route('/hello')
def hello(name=None):
     return render_template('hello.html', name=name)


if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    if (os.environ['deployEnv'] == "production"):
        app.run(host='0.0.0.0', port=os.environ['PORT'])
    else:
        app.run(host=os.environ['myIP'],debug=True)
        
    