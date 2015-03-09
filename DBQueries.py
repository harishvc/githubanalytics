#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from pymongo import MongoClient
import os.path, time
from flask import Flask
import re
import datetime
import collections

#Local modules
import RandomQuotes
import Neo4jQueries
import MyMoment
import sys

app = Flask(__name__)

#Set encoding 
reload(sys)
sys.setdefaultencoding("utf-8")

#Configure for production or development based on environment variables
if (os.environ['deployEnv'] == "production"):
    MONGO_URL = os.environ['connectURLRead']
    connection = MongoClient(MONGO_URL)
    db = connection.githublive.pushevent
else: 
    MONGO_URL = os.environ['connectURLReaddev']
    connection = MongoClient(MONGO_URL)
    db = connection.githubdev.pushevent

    
#Global variables
DefaultLimit=10
SearchLimit = 10
TypeaheadLimit = 10
ULS = "<ul class=\"list-group\">"
ULE = "</ul>"
LIS = "<li class=\"list-group-item\">"
LISNBP = "<li class=\"list-group-item nbp\">"
LIS2 = "<li class=\"list-group-item2\">"
LIE = "</li>"
SB12 = "<div class=\"col-sm-12 clearfloat\">"
#SB12 = "<div class=\"col-sm-12\" style=\"float:none;\">"
SB5  = "<div class=\"col-sm-5\">"
SB7  = "<div class=\"col-sm-7\">"
DE = "</div>"
LGIHS = "<h3 class=\"list-group-item-heading text-success\">"
LGIHE = "</h3>" 
#z1 = """<h3 class="list-group-item-heading">Similar Repositories</h3>"""
#z2 = """<p class="list-group-item-text2 nav nav-pills nav-stacked">"""
#z3 ="</p>"
#tz1 = """<div class="clearfix visible-xs"></div>
#    <div class="clearfix visible-sm"></div>"""
        
def ProcessQuery(query):
    if (query == ""):
        return "EMPTY"
    else: 
        app.logger.debug("processing ............ ->%s<-" ,  query)
        if (query == "total repositories"):
             return FindDistinct ('PushEvent','full_name','$full_name',"repositories")
        elif (query == "total users"):
             return FindDistinct ('PushEvent','actors','$actorlogin', "users")
        elif (query == "total new repositories"):
             return FindDistinct ('CreateEvent','full_name','$full_name',"new repositories")
        elif  (query == "total active users"):
            return FindDistinct ('PushEvent','actors','$actorlogin', "users")
        elif  (query == "total commits"):   
            return TotalEntries("commits")
        elif  (query.startswith("repository")):
            return ProcessRepositories(query.replace('repository ', ''))
        elif  (query == "trending now"):
            return (TrendingNow())
        elif  (query == "user commit frequency"):
            return (CommitFrequency("User commit frequency"))
        elif  (query == "top repositories sorted by contributors"):
            return (ReportTopRepositoriesBy("Top repositories sorted by contributors","authors","all"))
        elif  (query == "top repositories sorted by commits"):
            return (ReportTopRepositoriesBy("Top repositories sorted by commits","total","all"))
        elif  (query == "top repositories sorted by branches"):
            return (ReportTopRepositoriesBy("Top repositories sorted by branches","branches","all"))
        elif  (query == "top new repositories sorted by contributors"):
            return (ReportTopRepositoriesBy("Top new repositories sorted by contributors","authors","new"))
        elif  (query == "top new repositories sorted by commits"):
            return (ReportTopRepositoriesBy("Top new repositories sorted by commits","total","new"))
        elif  (query == "top new repositories sorted by branches"):
            return (ReportTopRepositoriesBy("Top new repositories sorted by branches","branches","new"))
        else:
            #return ("EMPTY")
            #Global Search
            return Search(query) 
        
def numformat(value):
    return "{:,}".format(value)

def TotalEntries (type):
    return ("<div class=\"digital\">" + numformat(db.count()) + "</div> " + type)

def FindDistinct(match,field,fieldName,type):
    pipeline= [
           { "$match": {"type": match }},     
           { '$group': { '_id': { field : fieldName}}},
           { '$group': { '_id': 1, 'count': { '$sum': 1 }}}
           ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        return ("<div class=\"digital\">" + numformat(row['count']+1) + "</div> " + type)
        
def CheckNewRepo(r):
    return (db.find_one({"type":"CreateEvent","full_name":r}))

def ProcessRepositories(repoName):
    #TODO: Add header
    sh = "<h2></h2>"
    mycursor = RepoQuery(repoName)
    SR = Neo4jQueries.FindSimilarRepositories(repoName)
    if (len(mycursor["result"]) == 0):
        return ("EMPTY")
    else:       
        myreturn =""   
        for record in mycursor["result"]:
            myreturn = sh + ULS
            myreturn += LIS + SB5 + "<a href=" + str(record['url']) + ">" + str(record['name']) + "</a>" + DE + SB7
            #myreturn += "&nbsp;&nbsp;&nbsp;"+ "<i class=\"fa fa-code fa-1x\"></i>&nbsp;"+ str(record['language'])
            if (record['count'] > 1): 
                myreturn += "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + numformat(record['count']) + " commits"
            else:
                myreturn += "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + str(record['count']) + " commit"
            if (len(record['refc']) > 1):
                myreturn += "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(record['refc'])) + " branches"
            else:
                myreturn += "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(record['refc'])) + " branch"    
            if (len(record['actorname']) > 1):
                myreturn += "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(record['actorname'])) + " contributers"
            else:
                myreturn += "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(record['actorname'])) + " contributer"   
            if(record['organization'] != 'Unspecified'):  myreturn += "<i class=\"lrpadding fa fa-home fa-1x\"></i>&nbsp;" + str(record['organization']) 
            myreturn += DE + LIE            
            #Handle None & empty description
            if ('description' in record):
                if ( (record['description'] != None) and (len(record['description'])) > 0):
                    myreturn += LIS + SB12 + record['description'].encode('utf-8').strip() + DE + LIE
                    #print "Description is not empty -->" , record['description']
            
            #Similar repositories        
            if (len(SR) > 0):
                #myreturn += LIS + ULS + LIS2 + SB12 + SR + LIE + ULE + DE + LIE
                #myreturn += LIS +  tz1 + SB12 + z1 + z2 + SR + z3 + DE + LIE
                myreturn += LISNBP + SB12 + LGIHS + "Similar" + LGIHE + SR  + DE + LIE
            
            # Show contributors using list group badges
            myreturn += "<a href=\"#\" class=\"list-group-item nbp\" data-toggle=\"collapse\" data-target=\"#contributors\">" + SB12
            myreturn += LGIHS + "Contributors&nbsp;&nbsp;" + "<span class=\"badge\">" + str(len(record['actorname'])) + "</div></span>" 
            myreturn += "<div id=\"contributors\" class=\"collapse\">" + "<p class=\"cstyle\">" + ', '.join(record['actorname']).encode('ascii', 'ignore').strip() + "</p></div></a>" + LGIHE 

            #Group by hours to create accordion using panels            
            CD = collections.OrderedDict()
            for x in record["comment"]:
                created_at =  int(record["created_at"].pop(0)/1000)
                key = MyMoment.HTH(created_at)
                sha = record['sha'].pop(0).encode('utf-8').strip()
                value = "<p><a href=" + str(record['url']) + "/commit/" + sha + ">[" + sha[0:7] + "]</a>"
                value += "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i> branch:" + str(record['ref'].pop(0).replace('refs/heads/','')) 
                value += "&nbsp;&nbsp;" + x.encode('utf-8').strip() + "</p>"                  
                if key in CD.keys():
                    tmp = CD[key] + value
                    CD[key] = tmp
                else:
                    CD[key] = value    
            
            myreturn += "<li class=\"list-group-item nbp\">" + SB12 + LGIHS + "Comments" + LGIHE + "<div class=\"panel-group\" id=\"accordion\">"
            for k, v in CD.items():
               h = str(k) + " hours" if (int(k) > 1) else  str(k) + " hour" if (int(k) == 1) else "<1 hour"
               myreturn += "<div class=\"panel panel-default\"><div class=\"panel-heading\">"
               myreturn +=  "<p class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#accordion\" href=\"#" + str(k) + "\">"+  h + " ago</a></p></div>"
               myreturn +=  "<div id=\"" + str(k) + "\" class=\"panel-collapse collapse\"><div class=\"panel-body\">" + v + "</div></div></div>" 
            myreturn +=  "</div></li>" + ULE

        return(myreturn)


#Find information about a repository   
def RepoQuery (repoURL):
    pipeline= [
           #{ '$match' : { 'url' : repoURL , 'sha': { '$exists': True }}  },
           { '$match' : { 'full_name' : repoURL , 'sha': { '$exists': True }}  },
           { '$sort': {'created_at': -1}},
           { '$group': {'_id': {'url': '$url',  'name': "$name", 'language': "$language",'description': "$description",'organization': '$organization'}, '_a1': {"$addToSet": "$actorname"} ,'_a2': {"$push": "$comment"},'_a3': {"$push": "$created_at"},'_a4': {"$push": "$sha"},'_a5': {"$push": "$ref"},'_a6': {"$addToSet": "$ref"},'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'count': '$count',  'name': "$_id.name", 'language': "$_id.language",'description': "$_id.description", 'actorname': "$_a1",'comment': "$_a2",'created_at': "$_a3", 'sha': "$_a4" ,'ref': "$_a5" ,'refc': "$_a6",'organization': { '$ifNull': [ "$_id.organization", "Unspecified"]}}},
           ]
    mycursor = db.aggregate(pipeline)
    
    #Debug
    #for row in mycursor["result"]:
        #print row
        
    return mycursor

#Modified from http://www.saltycrane.com/blog/2007/10/using-pythons-finditer-to-highlight/
#Highlight Search Results
def HSR(regex,text):
    #COLOR = ['yellow']
    i = 0; output = ""
    for m in regex.finditer(text):
        #output += "".join([text[i:m.start()],"<span class='highlight'>", text[m.start():m.end()],"</span>"])
        output += "".join([text[i:m.start()],"<mark>", text[m.start():m.end()],"</mark>"])
        i = m.end()
    return ("".join([output, text[i:]])) 
    
       
    
#Global search using MongoDB index on field name
def Search(query):
    path1 = "<a href=\"/?q=repository "
    path2 = "&amp;action=Search\">"
    path3 = "</a>"
    output = ""
    qregx =""
    #d1 ="<div class=\"col-sm-5\">"
    #d2 ="<div class=\"col-sm-7\">"
    #d3 = "</div>"
    nwords = []
    #Query Start Time in milliseconds
    QST = int(datetime.datetime.now().strftime("%s"))
    #Handle query with more than one word and spaces between words
    words = query.split()
    for word in words:
        #Handle special characters in query
        nwords.append(re.escape(word))
    qregx = re.compile('|'.join(nwords), re.IGNORECASE)
    #Aggregation based on index score
    pipeline = [
           { '$match': { '$text': { '$search': query }, 'type':'PushEvent' }},
           { '$group':  {'_id': {'url': '$url',  'full_name': "$full_name", 'language': "$language",'description': "$description",'organization': '$organization','score': { '$meta': "textScore" }},'_a1': {"$addToSet": "$actorname"},'_a2': {"$push": "$comment"},'_a3': {"$addToSet": "$ref"},'_a4': {"$push": "$ref"},'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'full_name': "$_id.full_name", 'count': '$count', 'language': "$_id.language",'description': "$_id.description",'score': "$_id.score",'organization': { '$ifNull': [ "$_id.organization", "Unspecified"]},'actorname': "$_a1",'ref': '$_a3'}},
           { '$sort':  { 'score': -1, 'count': -1}}
           ]
    
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    #Search results header 
    #print "Found .....", len(mycursor['result']) , " search matches ...."
    if (len(mycursor['result']) > SearchLimit):
        sh = "<p class=\"tpadding text-success\">Top " + str(SearchLimit) + " matches (found " + str(numformat(len(mycursor['result'])))  +  " matches in " + str(MyMoment.HTM(QST,"")).strip() +")</p>"
    else:
        sh = "<p class=\"tpadding text-success\">" + str(len(mycursor['result']))  + " matches (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>"
    
    
    totalSearchResults = 0
    for row in mycursor["result"]:
        tmp0=""
        totalSearchResults += 1
        if (totalSearchResults > SearchLimit):
            break
        else:
            tmp0 = "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + numformat(row['count']) + " commits" if (row['count'] > 1) else "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + str(row['count']) + " commit"
            tmp1 = "<i class=\"lrpadding fa fa-code fa-1x\"></i >" + HSR(qregx,row['language'].encode('utf-8').strip()) if (row['language']) else ""
            tmp2 = "<i class=\"lrpadding fa fa-home fa-1x\"></i>" + HSR(qregx,str(row['organization'])) if (row['organization'] != 'Unspecified') else ""
            tmp3 = "<br/>" + HSR(qregx,row['description'].encode('utf-8').strip()) if(row['description']) else ""
            tmp4 = "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(row['actorname'])) + " contributors" if (len(row['actorname']) > 1) else "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(row['actorname'])) + " contributor"
            tmp5 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branches" if (len(row['ref']) > 1) else "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branch"
            output += "<li class=\"list-group-item\">" + SB5 + path1 + row['full_name'].encode('utf-8').strip() + path2 + HSR(qregx, row['full_name'].encode('utf-8').strip()) + path3 + DE + SB7 + tmp0 + tmp5 + tmp4 + tmp1 + tmp2 + tmp3+ DE + "</li>"
            #TODO
            #output += Neo4jQueries.FindSimilarRepositories(row['url'])
            #output += FindSimilarRepositories(row['url'])
    if (len(output) > 0 ): 
        return ( sh + "<ul class=\"list-group\">" + output + "</ul>")
    else:
        return ("EMPTY")  #0 rows return


def TrendingNow():    
    sh = "<h2 class=\"text-success\">Trending repositories</h2>"
    output =""
    pipeline = [
                { '$match': {'type':'WatchEvent'}}, 
                { '$group': {'_id': {'full_name': '$full_name'}, 'stars': { '$sum' : 1 }}},
                { '$project': { '_id': 0, 'full_name': '$_id.full_name', 'stars': '$stars' } },
                { '$sort' : { 'stars': -1 }},
                { '$limit': DefaultLimit}
               ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        tmp0 = "<i class=\"lrpadding fa fa-star fa-1x\"></i>" + numformat(row['stars']) + " stars"
        output +=  LIS + SB12 + "<a href=\"https://www.github.com/" +  row['full_name'].encode('utf-8').strip() + "\">" + row['full_name'].encode('utf-8').strip() + "</a>" + tmp0 + DE + LIE
            
    return ( sh + ULS + output  + ULE)


def ReportTopRepositoriesBy(heading,sortBy,type):
    sh = "<h2 class=\"text-success\">" + heading + "</h2>"
    path1 = "<a href=\"/?q=repository "
    path2 = "&amp;action=Search\">"
    path3 = "</a>"
    output =""
    t2 = "class=\"list-group-item\""
    NewQuery =  "CreateEvent"
    if (type == "all"):
        pipeline= [
                   { '$match': {"$or" : [ {"type": {"$in": ["PushEvent"]}}, {"type": {"$in": ["CreateEvent"]}}, {"type": {"$in": ["WatchEvent"]}} ]}},
                   { "$group": {"_id": {"full_name": "$full_name", "organization": "$organization"},"authoremails":{"$addToSet":"$actoremail"}, \
                                "ref":{"$addToSet":"$ref"}, "type":{"$addToSet":"$type"}, \
                                "total": { "$sum": {"$cond": [ {"$eq": ['$type', 'PushEvent']}, 1, "null" ]}}, \
                                "stars": { "$sum": {"$cond": [ {"$eq": ['$type', 'WatchEvent']}, 1, "null" ]}} }}, \
                   { "$project": {"_id":0,"full_name":"$_id.full_name","organization":"$_id.organization","stars":"$stars", "type":"$type","total": "$total","branches":{"$size":"$ref"},"authors":{"$size":"$authoremails"}}},
                   { "$sort" : { sortBy: -1}},
                   { "$limit": DefaultLimit} 
                   ]
    elif (type == "new"):
        pipeline= [
                   { '$match': {"$or" : [ {"type": {"$in": ["PushEvent"]}}, {"type": {"$in": ["CreateEvent"]}}, {"type": {"$in": ["WatchEvent"]}} ]}},
                   { "$group": {"_id": {"full_name": "$full_name", "organization": "$organization"},"authoremails":{"$addToSet":"$actoremail"}, \
                                "ref":{"$addToSet":"$ref"}, "type":{"$addToSet":"$type"}, \
                                "total": { "$sum": {"$cond": [ {"$eq": ['$type', 'PushEvent']}, 1, "null" ]}}, \
                                "stars": { "$sum": {"$cond": [ {"$eq": ['$type', 'WatchEvent']}, 1, "null" ]}} }}, \
                   { "$project": {"_id":0,"full_name":"$_id.full_name","organization":"$_id.organization","stars":"$stars", "type":"$type","total": "$total","branches":{"$size":"$ref"},"authors":{"$size":"$authoremails"}}},
                   { "$match": {"type": {"$in": ["CreateEvent"]}}}, 
                   { "$sort" : { sortBy: -1}},
                   { "$limit": DefaultLimit} 
                   ]        
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        tmp0 = "<i class=\"lrpadding fa fa-star fa-1x\"></i>" + numformat(row['stars']) + " stars" if (int(row['stars']) > 1) else "<i class=\"lrpadding fa fa-star fa-1x\"></i>1 star" if (int(row['stars']) == 1)  else ""
        tmp1 = "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + numformat(row['total']) + " commits"
        tmp2 =  "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(row['branches']) + " branches" if ( int(row['branches']) > 1) else "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + "1 branch"        #tmp2 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(row['branches']) + " branches"    
        tmp3 =  "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors" if ( int(row['authors']) > 1) else "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + "1 contributor"
        tmp4 = "<i class=\"lrpadding fa fa-home fa-1x\"></i>" + str(row['organization']) if ('organization' in row.keys()) else "" 
        tmp5 = "<sup><i class=\"rpadding fa fa-bullhorn fa-1x\">New</i></sup>" if ('CreateEvent' in row['type']) else "" 
        output += LIS + SB5 + path1 + row['full_name'].encode('utf-8').strip() + path2 + row['full_name'].encode('utf-8').strip() + path3 + tmp5 + DE + SB7 + tmp0 + tmp1 + tmp2 + tmp3  + tmp4 + DE + LIE
            
    return ( sh + ULS + output  + ULE)



def Typeahead(q):
    #Query Start Time in milliseconds
    #QST = int(datetime.datetime.now().strftime("%s"))
    regx1 = re.compile(q, re.IGNORECASE)
    pipeline= [
               {'$match': {'$and': [ {'type': {'$in': ["PushEvent"]}},{'full_name':regx1}] }}, 
               { "$limit": TypeaheadLimit}, 
               { "$group": {"_id": {"full_name": "$full_name"}}}, 
               { "$project": {"_id":0,"value": { "$concat": ["repository ","$_id.full_name"]}}}
               ]
    mycursor = db.aggregate(pipeline)    
    #print "processing time ...." + str(MyMoment.HTM(QST,"")).strip() 
    return (mycursor['result'])

  
def CommitFrequency (heading):
    sh = "<h2 class=\"text-success\">" + heading + "</h2>"
    range0 = range1 = range2 = range3 = range4 = range5 = range6 = 0
    pipeline= [
           { '$group': {'_id': '$actorlogin', 'commits': { '$sum' : 1 }}},
           { '$group': {'_id': '$commits', 'frequency': { '$sum' : 1 }}},
           { '$sort' : { '_id': -1 }}
           ]
    mycursor = db.aggregate(pipeline)
    #Group in multiples of 5
    for record in mycursor["result"]:
        if (record['_id']  == 1):
            range0 += record['frequency']
        elif (record['_id'] > 1 and (record['_id'] <= 3)):
            range1 += record['frequency']    
        elif (record['_id'] > 3 and (record['_id'] <= 5)):
            range2 += record['frequency']
        elif (record['_id'] > 5) and (record['_id'] <= 10):
            range3 += record['frequency']
        elif(record['_id'] > 10 and record['_id'] <= 15):
            range4 += record['frequency']
        elif(record['_id'] > 15 and record['_id'] <= 20):
            range5 += record['frequency']
        else:
            range6 += record['frequency'] 
    total = range0 + range1 + range2 + range3 + range4 + range5  
    output = sh + "<p>" +  FindDistinct ('PushEvent','actors','$actorlogin', "users") + "</p>"
    output += "<table class=\"table table-striped\"><tr><th>Commits per user</th><th>Users</th><th>% Users</th></tr>"
    output += "<tr><td>1</td><td>"     + numformat(range0) + "</td><td>" + "{0:.2f}".format(range0*100/ float(total)) + "%</td></tr>"
    output += "<tr><td>2-3</td><td>"   + numformat(range1) + "</td><td>" + "{0:.2f}".format(range1*100/ float(total)) + "%</td></tr>"
    output += "<tr><td>4-5</td><td>"   + numformat(range2) + "</td><td>" + "{0:.2f}".format(range2*100/ float(total)) + "%</td></tr>"
    output += "<tr><td>6-10</td><td>"  + numformat(range3) + "</td><td>" + "{0:.2f}".format(range3*100/ float(total)) + "%</td></tr>"
    output += "<tr><td>11-15</td><td>" + numformat(range4) + "</td><td>" + "{0:.2f}".format(range4*100/ float(total)) + "%</td></tr>"
    output += "<tr><td>16-20</td><td>" + numformat(range5) + "</td><td>" + "{0:.2f}".format(range5*100/ float(total)) + "%</td></tr>" 
    output += "<tr><td>>20</td><td>"   + numformat(range6) + "</td><td>" + "{0:.2f}".format(range6*100/ float(total)) + "%</td></tr></table>" 
    return output



    
def CloseDB():
    connection.close()