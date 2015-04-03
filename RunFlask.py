#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from flask import Flask, make_response, send_from_directory
from flask import request
from flask import jsonify
from flask import render_template
from datetime import datetime, timedelta
import json
import os.path, time
from jinja2 import Template
import HTMLParser
from json import loads
import bleach
from json import dumps

#Local modules
import Suggestions
import DBQueries
import Neo4jQueries     

#Global variables
NORESULT="<h2 class=\"searchstatus text-danger\">You've got me stumped!</h2>"    #No result

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
                t1 = Suggestions.compare("now") if (query == "") else Suggestions.compare(query)  
                processed_text1 =  NORESULT + t1
    else:
        query =""
        processed_text1 =""
            
    return render_template("index-bootstrap.html",
        title = 'Ask GitHub',
        showGAcode = os.environ['showGAcode'],
        appenv = os.environ['deployEnv'],
        query = [{"text": query}],     
        processed_text = processed_text1)
    

@app.route('/_findsimilarrepositories')
def findsimilarrepositories():
    reponame = bleach.clean(request.args['a']).strip()
    SR = Neo4jQueries.FindSimilarRepositories(reponame)
    return jsonify(similarrepos=SR)

@app.route('/_listlanguages')
def listlanguages():
    reponame = bleach.clean(request.args['a']).strip()
    #TODO: Handle empty reponame
    Languages = DBQueries.LanguageBreakdown(reponame)
    return jsonify(languages=Languages)


#TEST
#@app.route('/test/')
#def test():
#    return render_template("test.html")

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
@app.route('/tsearch')
def tsearch(name=None):
    query = bleach.clean(request.args['q']).strip()
    #print query
    #Minimum 5 characters for query 
    if (len(query) <= 4 ): 
        t = [] #return nothing!
    else:
        t = DBQueries.Typeahead(query) 
       
    return make_response(dumps(t))
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

if __name__ == '__main__':
    if (os.environ['deployEnv'] == "production"):
        app.run(host='0.0.0.0', port=os.environ['PORT']) 
    else:
        app.run(host=os.environ['myIP'],debug=True)