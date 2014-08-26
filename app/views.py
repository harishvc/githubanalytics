#Source: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates

from flask import render_template
from app import app
import json
from datetime import datetime, timedelta
import os.path, time
import operator

# configuration
json_data=open('./app/data/PushEvent.json')
data = json.load(json_data)
DEBUG = True
#f = open(JSON_DATA, 'r')
#data = json.load(f)
#f.close()

#Global variables
#mydata = []
#now = time.ctime(os.path.getmtime(json_data))
now ="TODO"
numcommits = 0
languages = dict()
repositories= dict()
users= dict()
 
def find_term(term,type,max):
    #WORKS!!!
    d = dict()
    d2 = dict()
    for key, value in data.items():
        #print key,"============>" ,value[term]
        if value[term] in d:
            d[value[term]] += 1
        else:
            d[value[term]] = 1
         
    d2 = sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=type)[:max]
    for key, value in d2:
        print "%s: %s" % (key, value)
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




def refresh_data():
    #http://stackoverflow.com/questions/850795/clearing-python-lists
    #mydata[:] = [] #clear list on the module scope
    
    #Refresh
    #users = {}
    #repositories = {}    
    #languages = {}  
    
    #TODO: Timestamp not getting updated when JSON file changes. Read ONE TIME!!!!!
    now = None
    now = datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " PSD"
 
    #Commits
    global numcommits
    numcommits = len(data)  
    
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
        #data = mydata )
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404