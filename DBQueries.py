#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from pymongo import MongoClient
import os.path, time
from flask import Flask


#Local modules
import RandomQuotes
import Suggestions
import Neo4jQueries

app = Flask(__name__)

#Configure for production or development based on environment variables
if (os.environ['deployEnv'] == "production"):
    MONGO_URL = os.environ['connectURLRead']
    connection = MongoClient(MONGO_URL)
    db = connection.githublive.pusheventCapped
else: 
    MONGO_URL = os.environ['connectURLRead']
    connection = MongoClient(MONGO_URL)
    db = connection.githublive.pusheventCapped
    #DEV
    #MONGO_URL = os.environ['connectURLdev']
    #db = connection.githubdev.pushevent
     

#Global variables
LimitActiveLanguages=5
LimitActiveLanguagesBubble=10
LimitActiveRepositories=15
LimitActiveUsers=5

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
    
def ProcessRepositories(repoName):
    global ShowSuggestion
    mycursor = RepoQuery(repoName)
    if (len(mycursor["result"]) == 0):
        return ("EMPTY")
    else:       
        myreturn =""
        #Add recommendation using neo4j
        similarRepos = Neo4jQueries.FindSimilarRepositories(repoName)
        for record in mycursor["result"]:
            myreturn = "<a href=" + str(record['url']) + ">" + str(record['name']) + "</a>"
            myreturn += "&nbsp;Language: " + str(record['language']) + "&nbsp;#commits: " + str(record['count'])
            myreturn += "</br>" + record['description'].encode('utf-8').strip()
            myreturn += similarRepos
            myreturn += "</br><b>Commits from</b>: " +  ', '.join(record['actorname']).encode('utf-8').strip()
            myreturn += "</br><b>Comments</b>:<ul>" 
            for x in record["comment"]: 
                #convert milliseconds to seconds
                #pop first element in the array
                sha = record['sha'].pop(-1).encode('utf-8').strip()
                myreturn += "<li>" + time.strftime("%d %b %Y, %H:%M:%S", time.localtime(record["created_at"].pop(0)/1000.0)) \
                            +  "&nbsp;&nbsp; last commit " + "<a href=" + str(record['url']) + "/commit/" + sha + ">" + sha[0:10] + "</a>"\
                            + "</br>" + x.encode('utf-8').strip() + "</li>" 
            myreturn +="</ul>"
            #app.logger.debug (myreturn)
            
        #Add recommendation using neo4j
        #myreturn += Neo4jQueries.FindSimilarRepositories(repoName)
                    
        return(myreturn)
   
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
        else:
            return ("EMPTY") 
    
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

def RepoQuery (repoName):
    pipeline= [
           { '$match': {"name": repoName}}, 
           { '$group': {'_id': {'url': '$url',  'name': "$name", 'language': "$language",'description': "$description"}, '_a1': {"$addToSet": "$actorname"} ,'_a2': {"$push": "$comment"},'_a3': {"$push": "$created_at"},'_a4': {"$addToSet": "$sha"},'count': { '$sum' : 1 }}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'count': '$count',  'name': "$_id.name", 'language': "$_id.language",'description': "$_id.description", 'actorname': "$_a1",'comment': "$_a2",'created_at': "$_a3", 'sha': "$_a4" } },
           ]
    mycursor = db.aggregate(pipeline)
    return mycursor

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


def CloseDB():
    connection.close()

