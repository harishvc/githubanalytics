#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from flask import Flask, make_response, send_from_directory,render_template, g, current_app, request
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

#Pagination
from flask.ext.paginate import Pagination

#Local modules
import Suggestions
import DBQueries
import Neo4jQueries     
import GetPrismatic

#Global variables
NORESULT="<h2 class=\"searchstatus text-danger\">You've got me stumped!</h2>"    #No result
PER_PAGE = 10 #search results per page

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
    response2 = ""
    resultheading = ""
    #Debug
    #time.sleep(5)
    page, per_page, offset = get_page_items()    
    total = 0
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                format_total=True,
                                format_number=True,
                                )
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
            (total, resultheading,processed_text1,response2) = DBQueries.ProcessQuery(query,offset, per_page)
            pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                format_total=True,
                                format_number=True,
                                record_name='repositories',
                                )
            if (processed_text1 == "EMPTY") :
                t1 = Suggestions.compare("now") if (query == "") else Suggestions.compare(query)  
                processed_text1 =  NORESULT + t1
    else:
        query =""
        processed_text1 =""
        response2 = ""
    return render_template("index-bootstrap.html",
        page=page,
        total=total,
        per_page=per_page,
        pagination=pagination,                   
        title = 'Ask GitHub',
        showGAcode = os.environ['showGAcode'],
        appenv = os.environ['deployEnv'],
        query = [{"text": query}],
        resultheading = resultheading,
        response2 = response2,     
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

@app.route('/_findtrendingtopics')
def findtrendingtopics():
    qvalue = bleach.clean(request.args['qvalue']).strip()
    qtype = bleach.clean(request.args['qtype']).strip()
    TT = GetPrismatic.GetInterestTopics(qtype,qvalue)
    return jsonify(trendingtopics=TT)



def get_css_framework():
    return 'bootstrap3'
def get_link_size():
    return 'sm'  #option lg
def show_single_page_or_not():
    return False
def get_page_items():
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = PER_PAGE
    else:
        per_page = int(per_page)
    offset = (page - 1) * per_page
    return page, per_page, offset
def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'repositories')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )
    
    
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