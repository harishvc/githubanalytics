#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from flask import Flask
from flask import request
from flask import render_template
from datetime import datetime, timedelta
import json
import os.path, time
from jinja2 import Template
import HTMLParser
from json import loads
import bleach


#Local modules
import RandomQuotes
import Suggestions
import DBQueries     

#Global variables
ARA =[]
AR = []
ShowSuggestion=False                 #Show Suggestion
NORESULT="<div class=\"col-sm-12\"><p id=\"searchstatus\">You've got me stumped!</p></div>"    #No result


def Generate():
   global AR, ARA 
   AR , ARA = DBQueries.ActiveRepositoriesGroupedByDistinctUsers()[0:2]

#TODO
#http://stackoverflow.com/questions/850795/clearing-python-lists    
#def refresh_data():

app = Flask(__name__)

#Format integers with comma
@app.template_filter()
def numformat(value):
    return "{:,}".format(value)
app.jinja_env.filters['numformat'] = numformat
#############################   
#Handle homepage   
@app.route('/',methods=['GET'])
@app.route('/index',methods=['GET'])
def index():
    query = ""
    processed_text1  = ""
    global ShowSuggestion
    ShowSuggestion = False
    #Debug
    #time.sleep(5)
    if request.method == 'GET':
        if 'q' in request.args:
            app.logger.debug("query from user ===> %s<===", request.args['q'])
            #Sanitize & Remove trailing space
            query = bleach.clean(request.args['q']).strip()
            app.logger.debug("query from user after bleach ===> %s<===", query)
            #Start: Uncomment to trigger slow response time
            #app.logger.debug ("sleeping .....")
            #time.sleep(15)
            #app.logger.debug ("awake .....")
            #End: Uncomment to trigger slow response time
            processed_text1 = DBQueries.ProcessQuery(query)
            if (processed_text1 == "EMPTY") :
                processed_text1 = NORESULT
                ShowSuggestion = True
    else:
        query =""
        processed_text1 =""
            
    return render_template("index-bootstrap.html",
        title = 'Ask GitHub',
        appenv = os.environ['deployEnv'],
        query = [{"text": query}],     
        processed_text = processed_text1,
        qr = Suggestions.RandomQuerySuggestions() if (query == "" or bool(ShowSuggestion)) else "")
    
############################
#Handle charts    
#@app.route('/charts')
#@app.route('/charts/')
#def charts():
#    Generate()
#    return render_template("charts.html",
#        title = 'Ask GitHub',
#        LCA = DBQueries.ActiveLanguagesBubble(),
#        CF = DBQueries.CommitFrequency(),
#        ARA = ARA,
#        AR = AR
#        )

############################
#Handle errors        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(500)
def error(e):
    print e
    return render_template('500.html'), 500
@app.route('/hello')
def hello(name=None):
     return render_template('hello.html', name=name)

if __name__ == '__main__':
    if (os.environ['deployEnv'] == "production"):
        app.run(host='0.0.0.0', port=os.environ['PORT']) 
    else:
        app.run(host=os.environ['myIP'],debug=True)