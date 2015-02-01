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
LimitActiveLanguages=5
LimitActiveLanguagesBubble=10
LimitActiveRepositories=15
LimitActiveUsers=5
SearchLimit=20
DefaultLimit=10

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

def ActiveLanguages():
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

#Source:http://stackoverflow.com/questions/25861471/mongo-aggregation-distinct               

def ActiveRepositoriesGroupedByDistinctUsers ():
    users =[]
    commits =[]
    mycursor = []
    pipeline= [
           { "$group": {  "_id": {"repo": "$url", "actorlogin": "$actorlogin" ,'name': "$name", 'language': "$language" }, "commits": { "$sum": 1 }}},
           { "$group": {  "_id": {"repo": "$_id.repo", "name": "$_id.name", "language": "$_id.language"},"distinct_users": { "$sum": 1 },"total_commits": { "$sum": "$commits" }}},
           { "$project": { "_id": 0, "repo_url": "$_id.repo", "repo_name": "$_id.name", "language": "$_id.language", "distinct_users": "$distinct_users","total_commits": "$total_commits"}},
           { "$sort" : { "distinct_users": -1}},
           { "$limit": LimitActiveRepositories} 
           ]
    mycursor = db.aggregate(pipeline)
    
    for record in mycursor["result"]:
        users.append({"month": str(record["repo_url"]),"reponame": str(record["repo_name"]) ,"count": str(record["distinct_users"])})
        commits.append({"month": str(record["repo_url"]), "reponame": str(record["repo_name"]),"count": str(record["total_commits"])})                    
    
    t2 = [{"data":users,"name": "# Unique users"},{"data":commits,"name": "# Commits"} ]
    return mycursor, t2        

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

#Source:http://stackoverflow.com/questions/25840723/mongo-aggregation-grouped-by-sum

def CommitFrequency ():
    output =[]
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
    output.append({"commits": "1", "count": range0, "count2": numformat(range0)})        
    output.append({"commits": "2-3",  "count": range1, "count2": numformat(range1)})
    output.append({"commits": "4-5", "count": range2,"count2": numformat(range2)})
    output.append({"commits": "6-10", "count": range3,"count2": numformat(range3)})
    output.append({"commits": "11-15", "count": range4,"count2": numformat(range4)})
    output.append({"commits": "16-20", "count": range5,"count2": numformat(range5)})
    output.append({"commits": ">20", "count": range6,"count2": numformat(range6)})
    return output

###################################################
####################################################    



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
            return SearchRepositoriesBy("WatchEvent","stars")
        else:
            #return ("EMPTY")
            #Global Search
            return Search(query) 
        
        
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
            if(record['organization'] != 'Unspecified'):  myreturn += "<i class=\"lrpadding fa fa-home fa-1x\"></i>&nbsp;" + str(record['organization']) 
            if (len(record['actorname']) > 1):
                myreturn += "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(record['actorname'])) + " contributers"
            else:
                myreturn += "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(record['actorname'])) + " contributer"   
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

#Find similar repositories
def FindSimilarRepositories(repoURL):
    output = ""
    pipeline= [
           { '$match': {"url": repoURL, "type" : "similarrepositories"}}, 
           { '$group': {'_id': {'similar': '$similar'}}},
           { '$project': { '_id': 0, 'similar': '$_id.similar'}},
           ]
    mycursor = db.aggregate(pipeline)
    for record in mycursor["result"]:
        output = str(record['similar'])
        
    if len(output) !=0 :
        return ("<br/><b>Similar Repositories</b>: " + output)
    else:
        return output

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
    #Aggregation based on regular expression
    pipelineOLD = [
           { '$match': {'$or' : [{'name':qregx},{'description':qregx},{ 'language': qregx },{ 'organization': qregx }] , 'sha': { '$exists': True } }},
           { '$group':  {'_id': {'url': '$url',  'name': "$name", 'language': "$language",'description': "$description",'organization': '$organization'}, '_a1': {"$addToSet": "$actorname"},'_a2': {"$push": "$comment"},'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'name': "$_id.name", 'count': '$count', 'language': "$_id.language",'description': "$_id.description", 'organization': { '$ifNull': [ "$_id.organization", "Unspecified"]}}},
           { '$sort' : { 'name': 1 }},
           { '$limit': SearchLimit}
           ]
    #Aggregation based on index score
    pipeline = [
           { '$match': { '$text': { '$search': query }, 'type':'PushEvent' }},
           { '$group':  {'_id': {'url': '$url',  'name': "$name", 'language': "$language",'description': "$description",'organization': '$organization','score': { '$meta': "textScore" }},'_a1': {"$addToSet": "$actorname"},'_a2': {"$push": "$comment"},'_a3': {"$addToSet": "$ref"},'_a4': {"$push": "$ref"},'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'name': "$_id.name", 'count': '$count', 'language': "$_id.language",'description': "$_id.description",'score': "$_id.score",'organization': { '$ifNull': [ "$_id.organization", "Unspecified"]},'actorname': "$_a1",'ref': '$_a3'}},
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
            tmp4 = "<i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(row['actorname'])) + " contributers"
        else:
            tmp4 = "<i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(row['actorname'])) + " contributer"
        tmp5 = ""
        if (len(row['ref']) > 1):
            tmp5 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branches"
        else:
            tmp5 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(len(row['ref'])) + " branch"
        output += "<li>" + path1 + row['url'].encode('utf-8').strip() + path2 + HSR(qregx, row['name'].encode('utf-8').strip()) + path3 + tmp0 + tmp5 + tmp4 + tmp1 + tmp2 + tmp3 
        
        #output += Neo4jQueries.FindSimilarRepositories(row['url'])
        #output += FindSimilarRepositories(row['url'])
        output += "</li>"
    if (len(output) > 0 ): 
        #TODO: Highlight query in selection
        return ("<p><span class='digital'>" + numformat(totalSearchResults)  +  "</span> matches (" + str(MyMoment.HTM(QST,"")).strip() +")</p>" + "<ul>" + output + "</ul>")
    else:
        return ("EMPTY")  #0 rows return


def SearchRepositoriesBy(type,sortBy):
    path1 = "<a href=\"/?q=repository "
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
                    { "$group": {"_id": {"full_name": "$full_name"},"authoremails":{"$addToSet":"$actoremail"},"ref":{"$addToSet":"$ref"}, "total": { "$sum": 1 }}},
                    { "$project": {"_id":0,"full_name":"$_id.full_name","total": "$total","branches":{"$size":"$ref"},"authors":{"$size":"$authoremails"}}},
                    { "$sort" : {"authors":-1}},
                    { "$limit": DefaultLimit} 
                    ]
    mycursor = db.aggregate(pipeline)
    totalSearchResults = 0
    for row in mycursor["result"]:
        totalSearchResults = totalSearchResults + 1 
        tmp0=""
        #totalSearchResults = totalSearchResults + 1 
        if (row['stars'] > 1): 
                tmp0 = "<i class=\"lrpadding fa fa-star fa-1x\"></i>" + numformat(row['stars']) + " stars"
        else:
                tmp0= "<i class=\"lrpadding fa fa-star fa-1x\"></i>" + str(row['stars']) + " star"
        output += "<li><a href=\"http://www.github.com/" +  row['full_name'].encode('utf-8').strip() + "\">" + row['full_name'].encode('utf-8').strip() + "</a>" + tmp0 + "</li>" 
        
    return ("<p>Trending repositories in the past 24 hours</p><ul>" + output + "</ul>")


def CloseDB():
    connection.close()

