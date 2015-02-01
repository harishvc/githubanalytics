#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from pymongo import MongoClient
import os.path, time
from flask import Flask
import re
import datetime

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
            return ("<p>Trending repositories in the past 24 hours</p><ul>" + ReportRepositoriesBy("WatchEvent","stars") +  "</ul>")
        elif  (query == "top active repositories by contributors"):
            return ("<p>Top active repositories sorted by #contributors in the past 24 hours</p><ul>" + ReportRepositoriesBy("Active","authors") +  "</ul>")
        elif  (query == "top active repositories by commits"):
            return ("<p>Top active repositories sorted by #commits in the past 24 hours</p><ul>" + ReportRepositoriesBy("Active","total") +  "</ul>")
        elif  (query == "top active repositories by branches"):
            return ("<p>Top active repositories sorted by #branches in the past 24 hours</p><ul>" + ReportRepositoriesBy("Active","branches") +  "</ul>")
        else:
            #return ("EMPTY")
            #Global Search
            return Search(query) 
        
def numformat(value):
    return "{:,}".format(value)

def TotalEntries (type):
    return ("<div class=\"digital\">" + numformat(db.count()) + "</div> " + type)

        
def ProcessRepositories(repoName):
    global ShowSuggestion
    mycursor = RepoQuery(repoName)
    if (len(mycursor["result"]) == 0):
        return ("EMPTY")
    else:       
        myreturn =""
        #Add recommendation using neo4j
        #similarRepos = Neo4jQueries.FindSimilarRepositories(repoName)
        #similarRepos = FindSimilarRepositories(repoName)
        
        
        for record in mycursor["result"]:
            myreturn = "<a href=" + str(record['url']) + ">" + str(record['name']) + "</a>"
            #myreturn += "&nbsp;&nbsp;&nbsp;"+ "<i class=\"fa fa-code fa-1x\"></i>&nbsp;"+ str(record['language'])
            if (record['count'] > 1): 
                myreturn += "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + str(record['count']) + " commits"
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
            #Handle None & empty description
            if ('description' in record):
                if ( (record['description'] != None) and (len(record['description'])) > 0):
                    myreturn += "</br>" + record['description'].encode('utf-8').strip()
                    #print "Description is not empty -->" , record['description']
            
            #myreturn += similarRepos
            
            myreturn += "</br><b>Commits from</b>: " +  ', '.join(record['actorname']).encode('utf-8').strip()
            myreturn += "</br><b>Comments</b>:<ul>" 
            for x in record["comment"]: 
                #convert milliseconds to seconds
                #pop first element in the array
                sha = record['sha'].pop(0).encode('utf-8').strip()
                myreturn += "<li>" +  "<a href=" + str(record['url']) + "/commit/" + sha + ">" + MyMoment.HTM(int(record["created_at"].pop(0)/1000),"ago") + "</a>" \
                            + "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i> branch:" + str(record['ref'].pop(0).replace('refs/heads/','')) \
                            + "&nbsp;&nbsp;" + x.encode('utf-8').strip() + "</li>" 
            myreturn +="</ul>"
            #app.logger.debug (myreturn)
                    
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
    COLOR = ['yellow']
    i = 0; output = ""
    for m in regex.finditer(text):
        output += "".join([text[i:m.start()],"<span class='highlight'>", text[m.start():m.end()],"</span>"])
        i = m.end()
    return ("".join([output, text[i:]])) 
    
       
    
#Global search in property fields name, language & description
def Search(query):
    path1 = "<a href=\"/?q=repository "
    path2 = "&amp;action=Search\">"
    path3 = "</a>"
    output = ""
    qregx =""
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
                tmp0 = "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + str(row['count']) + " commits"
        else:
                tmp0= "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + str(row['count']) + " commit"
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
        output += "<li>" + path1 + row['url'].encode('utf-8').strip() + path2 + HSR(qregx, row['full_name'].encode('utf-8').strip()) + path3 + tmp0 + tmp5 + tmp4 + tmp1 + tmp2 + tmp3 
        #TODO
        #output += Neo4jQueries.FindSimilarRepositories(row['url'])
        #output += FindSimilarRepositories(row['url'])
        output += "</li>"
    if (len(output) > 0 ): 
        #TODO: Highlight query in selection
        return ("<p><span class='digital'>" + numformat(totalSearchResults)  +  "</span> matches (" + str(MyMoment.HTM(QST,"")).strip() +")</p>" + "<ul>" + output + "</ul>")
    else:
        return ("EMPTY")  #0 rows return


def ReportRepositoriesBy(type,sortBy):
    path1 = "<a href=\"/?q=repository http://github.com/"
    path2 = "&amp;action=Search\">"
    path3 = "</a>"
    output =""
    pipeline =[]
    if type in ('WatchEvent' or 'PushEvent'):
        pipeline = [
                   { '$match': {'type':type}}, 
                   { '$group': {'_id': {'full_name': '$full_name'}, 'stars': { '$sum' : 1 }}},
                   { '$project': { '_id': 0, 'full_name': '$_id.full_name', 'stars': '$stars' } },
                   { '$sort' : { sortBy: -1 }},
                   { '$limit': DefaultLimit}
                   ]
    elif (type == 'Active'):
        pipeline= [
                    { '$match': {'type':'PushEvent'}},
                    { "$group": {"_id": {"full_name": "$full_name", "organization": "$organization"},"authoremails":{"$addToSet":"$actoremail"},"ref":{"$addToSet":"$ref"}, "total": { "$sum": 1 }}},
                    { "$project": {"_id":0,"full_name":"$_id.full_name","organization":"$_id.organization","total": "$total","branches":{"$size":"$ref"},"authors":{"$size":"$authoremails"}}},
                    { "$sort" : {sortBy:-1}},
                    { "$limit": DefaultLimit} 
                    ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        if (type == 'WatchEvent'):
            tmp0 = "<i class=\"lrpadding fa fa-star fa-1x\"></i>" + numformat(row['stars']) + " stars"
            output += "<li><a href=\"http://www.github.com/" +  row['full_name'].encode('utf-8').strip() + "\">" + row['full_name'].encode('utf-8').strip() + "</a>" + tmp0 + "</li>" 
        else:
            tmp0 = "<i class=\"lrpadding fa fa-clock-o fa-1x\"></i>" + str(row['total']) + " commits"
            tmp1 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(row['branches']) + " branches"    
            tmp2 = "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors"
            tmp4 = ""
            if('organization' in row): tmp4 = "<i class=\"lrpadding fa fa-home fa-1x\"></i>" + str(row['organization'])
            output += "<li>" + path1 + row['full_name'].encode('utf-8').strip() + path2 + row['full_name'].encode('utf-8').strip() + path3 + tmp0 + tmp1 + tmp2  + tmp4 + "</li>"
            
    return output


def CloseDB():
    connection.close()

