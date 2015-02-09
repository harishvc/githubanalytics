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
import Suggestions
import Neo4jQueries
import MyMoment

app = Flask(__name__)

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
ULS = "<ul class=\"list-group\">"
ULE = "</ul>"
LIS = "<li class=\"list-group-item\">"
LIE = "</li>"
SB12 = "<div class=\"col-sm-12\">"
SB5  = "<div class=\"col-sm-5\">"
SB7  = "<div class=\"col-sm-7\">"
DE = "</div>"
    
def ProcessQuery(query):
    global ShowSuggestion
    ShowSuggestion = False
    if (query == ""):
        return ""
    else: 
        app.logger.debug("processing ............ ->%s<-" ,  query)
        if (query == "active repositories"):
             return FindDistinct ('$url',"repositories")
        elif  (query == "active users"):
            return FindDistinct ('$actorlogin', "users")
        elif  (query == "active languages"):   
            return FindDistinct ('$language', "languages") 
        elif  (query == "total commits"):   
            return TotalEntries("commits")
        elif  (query.startswith("repository")):
            return ProcessRepositories(query.replace('repository ', ''))
        elif  (query == "trending now"):
            return (TrendingNow())
        elif  (query == "top active repositories by contributors"):
            return (ReportTopRepositoriesBy("Top active repositories by contributors","authors"))
        elif  (query == "top active repositories by commits"):
            return (ReportTopRepositoriesBy("Top active repositories by commits","total"))
        elif  (query == "top active repositories by branches"):
            return (ReportTopRepositoriesBy("Top active repositories by branches","branches"))
        else:
            #return ("EMPTY")
            #Global Search
            return Search(query) 
        
def numformat(value):
    return "{:,}".format(value)

def TotalEntries (type):
    return ("<div class=\"digital\">" + numformat(db.count()) + "</div> " + type)

def FindDistinct(fieldName,type):
    pipeline= [
           { '$match': {} },    
           { '$group': { '_id': fieldName}},
           { '$group': { '_id': 1, 'count': { '$sum': 1 }}}
           ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        return ("<div class=\"digital\">" + numformat(row['count']) + "</div> " + type)
        
def CheckNewRepo(r):
    return (db.find_one({"type":"CreateEvent","full_name":r}))

def ProcessRepositories(repoName):
    #TODO: Add header
    sh = "<h2></h2>"
    mycursor = RepoQuery(repoName)
    if (len(mycursor["result"]) == 0):
        return ("EMPTY")
    else:       
        myreturn =""
        
        #TODO: Add recommendation using neo4j
        #similarRepos = Neo4jQueries.FindSimilarRepositories(repoName)
        #similarRepos = FindSimilarRepositories(repoName)
           
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
            #TODO
            #myreturn += similarRepos
            
            # Show contributors using list group badges
            myreturn += "<a href=\"#\" class=\"list-group-item\" data-toggle=\"collapse\" data-target=\"#contributors\">" + SB12
            myreturn += "Contributors <span class=\"badge\">" + str(len(record['actorname'])) + "</div></span>" 
            myreturn += "<div id=\"contributors\" class=\"collapse\">" + "<p class=\"cstyle\">" + ', '.join(record['actorname']).encode('utf-8').strip() + "</p></div></a>"

            #Group by hours to create accardion using panels            
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
            
            myreturn += "<li class=\"list-group-item\">" + SB12 + "Comments" + "<div class=\"panel-group\" id=\"accordion\">"
            for k, v in CD.items():
               h = " hours" if (int(k) > 1) else " hour"
               myreturn += "<div class=\"panel panel-default\"><div class=\"panel-heading\">"
               myreturn +=  "<p class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#accordion\" href=\"#" + str(k) + "\">"+ str(k) + h + " ago</a></p></div>"
               myreturn +=  "<div id=\"" + str(k) + "\" class=\"panel-collapse collapse\"><div class=\"panel-body\">" + v + "</div></div></div>" 
            myreturn +=  "</div></li>" + ULE

        return(myreturn)


#Find information about a repository   
def RepoQuery (repoURL):
    pipeline= [
           { '$match' : { 'url' : repoURL , 'sha': { '$exists': True }}  },
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
            #{ '$match': { 'score': { '$gt': 1.0 }}},
           { '$sort':  { 'score': -1, 'count': -1}}
           #{ '$limit': SearchLimit}
           ]
    
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    totalSearchResults = 0
    for row in mycursor["result"]:
        tmp0=""
        totalSearchResults = totalSearchResults + 1 
        if (row['count'] > 1): 
                tmp0 = "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + numformat(row['count']) + " commits"
        else:
                tmp0= "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + str(row['count']) + " commit"
        tmp1 = ""
        if(row['language']): tmp1 = "<i class=\"lrpadding fa fa-code fa-1x\"></i>" + HSR(qregx,row['language'].encode('utf-8').strip())
        tmp2 = ""
        if(row['organization'] != 'Unspecified'): tmp2 = "<i class=\"lrpadding fa fa-home fa-1x\"></i>" + HSR(qregx,str(row['organization']))
        tmp3 = ""
        if(row['description']): tmp3 = "<br/>" + HSR(qregx,row['description'].encode('utf-8').strip())
        tmp4 = ""
        if (len(row['actorname']) > 1):
            tmp4 = "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(row['actorname'])) + " contributors"
        else:
            tmp4 = "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(row['actorname'])) + " contributor"
        tmp5 = ""
        if (len(row['ref']) > 1):
            tmp5 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branches"
        else:
            tmp5 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branch"
        
        #output += "<li class=\"list-group-item\">" + d1 + path1 + row['url'].encode('utf-8').strip() + path2 + HSR(qregx, row['full_name'].encode('utf-8').strip()) + path3 + d3 + d2 + tmp0 + tmp5 + tmp4 + tmp1 + tmp2 + tmp3+ d3 
       
        output += "<li class=\"list-group-item\">" + SB5 + path1 + row['url'].encode('utf-8').strip() + path2 + HSR(qregx, row['full_name'].encode('utf-8').strip()) + path3 + DE + SB7 + tmp0 + tmp5 + tmp4 + tmp1 + tmp2 + tmp3+ DE 
       
       
        #TODO
        #output += Neo4jQueries.FindSimilarRepositories(row['url'])
        #output += FindSimilarRepositories(row['url'])
        output += "</li>"
    if (len(output) > 0 ): 
        #TODO: Highlight query in selection
        return ("<p class=\"tpadding text-success\">" + numformat(totalSearchResults)  +  " matches (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>" + "<ul class=\"list-group\">" + output + "</ul>")
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
        output +=  LIS + SB12 + "<a href=\"http://www.github.com/" +  row['full_name'].encode('utf-8').strip() + "\">" + row['full_name'].encode('utf-8').strip() + "</a>" + tmp0 + DE + LIE
            
    return ( sh + ULS + output  + ULE)


def ReportTopRepositoriesBy(heading,sortBy):
    sh = "<h2 class=\"text-success\">" + heading + "</h2>"
    path1 = "<a href=\"/?q=repository http://github.com/"
    path2 = "&amp;action=Search\">"
    path3 = "</a>"
    output =""
    t2 = "class=\"list-group-item\""
    pipeline= [
               { '$match': {'type':'PushEvent'}},
               { "$group": {"_id": {"full_name": "$full_name", "organization": "$organization"},"authoremails":{"$addToSet":"$actoremail"},"ref":{"$addToSet":"$ref"}, "total": { "$sum": 1 }}},
               { "$project": {"_id":0,"full_name":"$_id.full_name","organization":"$_id.organization","total": "$total","branches":{"$size":"$ref"},"authors":{"$size":"$authoremails"}}},
               { "$sort" : { sortBy: -1}},
               { "$limit": DefaultLimit} 
               ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        tmp1 = "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + numformat(row['total']) + " commits"
        tmp2 =  "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(row['branches']) + " branches" if ( int(row['branches']) > 1) else "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + "1 branch"
        #tmp2 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(row['branches']) + " branches"    
        tmp3 =  "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors" if ( int(row['authors']) > 1) else "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + "1 contributor"
        #tmp3 = "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors"
        tmp4 = "<i class=\"lrpadding fa fa-home fa-1x\"></i>" + str(row['organization']) if ('organization' in row.keys()) else "" 
        output += LIS + SB5 + path1 + row['full_name'].encode('utf-8').strip() + path2 + row['full_name'].encode('utf-8').strip() + path3 + DE + SB7 + tmp1 + tmp2 + tmp3  + tmp4 + DE + LIE
            
    return ( sh + ULS + output  + ULE)


def CloseDB():
    connection.close()