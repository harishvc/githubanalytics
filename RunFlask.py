#Source: https://github.com/mganache/helloapp/

from flask import Flask
from flask import render_template
from datetime import datetime, timedelta
import json
import os.path, time
import operator

# configuration
myfile='./data/PushEvent.json'
json_data=open(myfile)
data = json.load(json_data)
DEBUG = True

#Global variables
now = time.ctime(os.path.getmtime(myfile))
numcommits = 0
languages = dict()
repositories= dict()
users= dict()

def find_term(term,type,max):
    d = dict()
    d2 = dict()
    for key, value in data.items():
        #print key,"============>" ,value[term]
        if value[term] in d:
            d[value[term]] += 1
        else:
            d[value[term]] = 1
         
    d2 = sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=type)[:max]
    return d2
    

def find_active_repositories(what,max):
    d = {}
    term=what
    for key, value in data.items():
        if value[term] in d:
            d[value[term]]['count'] +=1            
        else:
            tmp1 = {'count':1,'name':value['name'],'url':value['url'],'language':value['name']}
            d[value[term]] = tmp1
            
    return sorted(d.iteritems(), key=lambda (x, y): (y['count']),reverse=True)[:max]

def find_active_users(what,max):
    d = {}
    term=what
    for key, value in data.items():
        if value[term] in d:
            d[value[term]]['count'] +=1            
        else:
            tmp1 = {'count':1,'actorname':value['actorname'],'actorlogin':value['actorlogin']}
            d[value[term]] = tmp1

    return sorted(d.iteritems(), key=lambda (x, y): (y['count']),reverse=True)[:max]


#http://stackoverflow.com/questions/850795/clearing-python-lists    
def refresh_data():
    global now
    now = time.ctime(os.path.getmtime(myfile)) + " PSD"
 
    #Commits
    global numcommits
    numcommits = "{:,}".format(len(data))  
    
    #Find Top Languages 
    #languages = dict()
    global languages
    languages = find_term("language",True,5)
    
    #Find active repositories
    global repositories
    repositories = find_active_repositories("url",5)
    
    #Find active users
    global users
    users = find_active_users("actorlogin",5)



app = Flask(__name__)
 
@app.route('/')
@app.route('/index')
def index():
    refresh_data()
    return render_template("index.html",
        title = 'GitHub Analytics',
        numcommits = numcommits,
        time  = now,
        languages = languages,
        repositories = repositories,
        users = users
        )
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.route('/hello')
def hello(name=None):
     return render_template('hello.html', name=name)


if __name__ == '__main__':
	app.run(debug=True)
