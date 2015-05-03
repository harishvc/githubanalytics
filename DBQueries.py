#References
#https://realpython.com/blog/python/primer-on-jinja-templating/

from pymongo import MongoClient
import os.path, time
from flask import Flask
import re
import datetime
import collections
import sys
import bleach

#Local modules
import RandomQuotes
import Neo4jQueries
import MyMoment

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
SB5  = "<div class=\"col-sm-5\">"
SB7  = "<div class=\"col-sm-7\">"
DE = "</div>"
LGIHS = "<h3 class=\"list-group-item-heading text-success\">"
LGIHE = "</h3>" 
        
def ProcessQuery(query,offset, per_page):
    if (query == ""):
        return "EMPTY"
    else: 
        app.logger.debug("processing ............ ->%s<-" ,  query)
        if (query == "total repositories"):
             return (0, FindDistinct ('PushEvent','full_name','$full_name',"repositories"))
        elif (query == "total users"):
             return (0, FindDistinct ('PushEvent','actors','$actorlogin', "users"))
        elif (query == "total new repositories"):
             return (0, FindDistinct ('CreateEvent','full_name','$full_name',"new repositories"))
        elif  (query == "total commits"):   
            return (0,TotalEntries("PushEvent","commits"))
        elif  (query == "trending now"):
            return (0,TrendingNow())
        elif  (query == "top repositories"):
            return (0, ReportTopRepositoriesBy("Top repositories sorted by contributors","authors","all"))
#         elif  (query == "top repositories sorted by commits"):
#             return (ReportTopRepositoriesBy("Top repositories sorted by commits","total","all"))
#         elif  (query == "top repositories sorted by branches"):
#             return (ReportTopRepositoriesBy("Top repositories sorted by branches","branches","all"))
        elif  (query == "top new repositories"):
            return (0, ReportTopRepositoriesBy("Top new repositories sorted by contributors","authors","new"))
#         elif  (query == "top new repositories sorted by commits"):
#             return (ReportTopRepositoriesBy("Top new repositories sorted by commits","total","new"))
#         elif  (query == "top new repositories sorted by branches"):
#             return (ReportTopRepositoriesBy("Top new repositories sorted by branches","branches","new"))
        elif  (query == "top organizations"):
             return (0, ReportTopOrganizations("Top Organizations"))
        elif  (query == "top contributors"):
            return (0, ReportTopContributors("Top Contributors"))
        elif  (query == "top languages"):
            return (0, ReportTopLanguages("Top Languages"))
        elif  (query.startswith("repository")):
            return (0,ProcessRepositories(query.replace('repository ', '')))  
        elif  (query.startswith("organization")):
            return Search(bleach.clean(query.replace('organization ', '').strip()),"organization",offset, per_page)
        elif  (query.startswith("language")):
            return Search(bleach.clean(query.replace('language ', '').strip()),"language",offset, per_page)
        elif  (query.startswith("contributor")):
            return (Search(bleach.clean(query.replace('contributor ', '').strip()),"contributor",offset, per_page))
        elif (query == "dashboard"):
            return (0, Dashboard("regular"))
        else:
            #Default
            return Search(query,"all",offset, per_page) 
        
def numformat(value):
    return "{:,}".format(value)

def TotalEntries (etype,type):
    if (type == "regular"):
        return (db.find({"type": etype}).count())
    else:
        return ("<div class=\"digital\">" + numformat(db.find({"type": etype}).count()) + "</div> " + type)

def FindDistinct(match,field,fieldName,type):
    pipeline= [
           { "$match": {"type": match }},     
           { '$group': { '_id': { field : fieldName}}},
           { '$group': { '_id': 1, 'count': { '$sum': 1 }}}
           ]
    mycursor = db.aggregate(pipeline)
    for row in mycursor["result"]:
        if (type == "regular"):
            return row['count']
        else: 
            return ("<div class=\"digital\">" + numformat(row['count']+1) + "</div> " + type)
        
def CheckNewRepo(r):
    return (db.find_one({"type":"CreateEvent","full_name":r}))

def ProcessRepositories(repoName):
    #TODO: Add header
    sh = "<h2></h2>"
    mycursor = RepoQuery(repoName)
    
    #Passing repository name as hidden input
    SR =  "<input type=\"hidden\" name=\"reponame\" value=" + repoName + "></input>\
          <span id=\"similarrepos\"></span><p><div id=\"wrapperfindsimilarrepos\"> \
          <button type=\"button\" class=\"btn btn-default\"><a href=\"javascript:void();\" id=\"findsimilarrepos\">Find similar repositorites</a></button></div>"
    
    #Place holder for languages loaded using AJAX
    LBD = "<div id=\"listlanguages\"></div>"
    
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
                myreturn += "<span class=\"nobr\"><i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(len(record['actorname'])) + " contributers</span>"
            else:
                myreturn += "<span class=\"nobr\"><i class=\"lrpadding fa fa-user fa-1x\"></i>" + str(len(record['actorname'])) + " contributer</span>"   
            if(record['organization'] != 'Unspecified'):  myreturn += "<span class=\"nobr\"><i class=\"lrpadding fa fa-home fa-1x\"></i>&nbsp;" + str(record['organization']) + "</span>" 
            myreturn += DE + LIE            
           
            #Handle None & empty description
            if ('description' in record):
                if ( (record['description'] != None) and (len(record['description'])) > 0):
                    myreturn += LIS + SB12 + record['description'].encode('utf-8').strip() + DE + LIE
                    #print "Description is not empty -->" , record['description']

            #Display languages
            if LBD:
                LBD.strip()
                myreturn += LISNBP + SB12 + LBD  + DE + LIE
             
            #Place holder for similar repositories: Invoked by user and driven by AJAX        
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
    i = 0; output = ""
    for m in regex.finditer(text):
        #output += "".join([text[i:m.start()],"<span class='highlight'>", text[m.start():m.end()],"</span>"])
        output += "".join([text[i:m.start()],"<mark>", text[m.start():m.end()],"</mark>"])
        i = m.end()
    output = "".join([output, text[i:]])
    #Handle long repository names
    if (len(output) > 60):
        return (output[0:45] + "...")
    else:    
        return output
     
#Global search using MongoDB index on field name
def Search(query,type,offset, per_page):
    path1 = "<a href=\"/?q=repository "
    path2 = "&amp;action=Search\" class=\"repositoryinfo\">"
    path3 = "</a>"
    output = ""
    qregx =""
    nwords = []
    sh = ""
    tt = ""  #Trending Topics
    #Query Start Time in milliseconds
    QST = int(datetime.datetime.now().strftime("%s"))
    #Handle query with more than one word and spaces between words
    words = query.split()
    for word in words:
        #Handle special characters in query
        nwords.append(re.escape(word))
    qregx = re.compile('|'.join(nwords), re.IGNORECASE)
    #Aggregation based on index score
    if (type == "organization"):
        pipeline = [
                    { '$match': {'$and': [ {'type': {'$in': ["PushEvent"]}},{'organization':query}] }}, 
                    { '$group':  {'_id': {'full_name': "$full_name", 'organization': '$organization'},'_a1': {"$addToSet": "$actorname"},'_a3': {"$addToSet": "$ref"},'count': { '$sum' : 1 }}},
                    { '$sort':  {'count': -1}},
                    { "$group" : {"_id" : 'null',"my_documents" : {"$push" : {"_id" : "$_id",'actorname':'$_a1','ref':'$_a3','count':"$count"}},"TOTAL" : {"$sum" : 1}}},
                    { "$unwind" : "$my_documents" },
                    { "$project" : {"_id" : 0,"my_documents" : 1,"TOTAL" : "$TOTAL"}},
                    { "$skip": offset},
                    { "$limit": per_page} 
                   ]
    elif (type == "contributor"):
        pipeline = [
                    { '$match': {'$and': [ {'type': {'$in': ["PushEvent"]}},{'actoremail':query}] }}, 
                    { '$group':  {'_id': {'full_name': "$full_name",'organization': { '$ifNull': [ "$organization", "Unspecified"]}},'_a1': {"$addToSet": "$actorname"},'_a3': {"$addToSet": "$ref"},'count': { '$sum' : 1 }}},
                    { '$sort':  {'count': -1}},
                    { "$group" : {"_id" : 'null',"my_documents" : {"$push" : {"_id" : "$_id",'actorname':'$_a1','ref':'$_a3','count':"$count"}},"TOTAL" : {"$sum" : 1}}},                    
                    { "$unwind" : "$my_documents" },
                    { "$project" : {"_id" : 0,"my_documents" : 1,"TOTAL" : "$TOTAL"}},
                    { "$skip": offset},
                    { "$limit": per_page} 
                   ]
    elif (type == "language"):
        #Step 1: Find all repositories
        pipeline= [
                { "$match": {"type": "RepoInfo2"}},
                { "$unwind" : "$language" },
                { "$match": {"language.l": { "$regex" : qregx }}},
                { "$project": {"_id":1,"full_name":"$full_name"}}  
               ]
        mycursor = db.aggregate(pipeline)
        ALLR = []         
        for row in mycursor["result"]: 
            ALLR.append(row['full_name'])    
        #Step 2: Gather more information about each repository
        pipeline = [
              { '$match': {'$and': [ {"type":"PushEvent"},{"full_name" : {'$in': ALLR}} ]}},
              { '$group':  {'_id': {'url': '$url',  'full_name': "$full_name",'organization': { '$ifNull': [ "$organization", "Unspecified"]}},'_a1': {"$addToSet": "$actorname"},'_a3': {"$addToSet": "$ref"},'count': { '$sum' : 1 }}},
              { '$sort':  {'count': -1}},
              { "$group" : {"_id" : 'null',"my_documents" : {"$push" : {"_id" : "$_id",'actorname':'$_a1','ref':'$_a3','count':"$count"}},"TOTAL" : {"$sum" : 1}}},                    
              { "$unwind" : "$my_documents" },
              { "$project" : {"_id" : 0,"my_documents" : 1,"TOTAL" : "$TOTAL"}},
              { "$skip": offset},
              { "$limit": per_page} 
              ]
 
    #Default search      
    else:
        pipeline = [
                    { '$match': { '$text': { '$search': query }, 'type':'PushEvent' }},
                    { '$group':  {'_id': {'full_name': '$full_name','organization': { '$ifNull': [ "$organization", "Unspecified"]},\
                                          'score': { '$meta': "textScore" }},'_a1': {"$addToSet": "$actorname"},'_a3': {"$addToSet": "$ref"},\
                                          'count': { '$sum' : 1 } }},
                    { "$group" : {"_id" : 'null',"my_documents" : {"$push" : {"_id" : "$_id",'actorname':'$_a1','ref':'$_a3','count':"$count"}},"TOTAL" : {"$sum" : 1}}},
                    { "$unwind" : "$my_documents" },
                    { "$project" : {"_id" : 0,"my_documents" : 1,"TOTAL" : "$TOTAL"}}, 
                    { '$sort':  { 'score': -1, 'count': -1}},
                    { "$skip": offset},
                    { "$limit": per_page}
                   ]    
    
    #PROCESS
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    
    total = 0
    for ritem in mycursor["result"]:
        total =  ritem['TOTAL']
        count = ritem['my_documents']['count']
        lactors = len(ritem['my_documents']['actorname'])
        lbranches = len(ritem['my_documents']['ref'])
        fn = ritem['my_documents']['_id']['full_name'].encode('utf-8').strip()
        tmp1 = "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>" + numformat(count) + " commits" if (count > 1) else "<i class=\"rpadding fa fa-clock-o fa-1x\"></i>1 commit"
        tmp2 = "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>" + str(lbranches) + " branches" if (lbranches > 1) else "<i class=\"lrpadding fa fa-code-fork fa-1x\"></i>1 branch"
        tmp3 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(lactors) + " contributors</span>" if (lactors > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-user fa-1x\"></i>1 contributor</span>"
        tmp4 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-home fa-1x\"></i>" + HSR(qregx,ritem['my_documents']['_id']['organization']) + "</span>" if ritem['my_documents']['_id']['organization']!= "Unspecified" else ""
        output += "<li class=\"list-group-item\">" + SB5 + path1  + fn + path2 + HSR(qregx,fn) + path3 + DE + SB7 + tmp1 + tmp2 + tmp3 + tmp4 + DE + "</li>"        
    
    if (len(output) > 0 ):
        if (type == "all"):
            sh = "<p class=\"tpadding text-success\">Repository matches (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>"
        elif (type == "organization"):
                sh = "<p class=\"tpadding text-success\">" + "Repositories inside organization " + query + " (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>"
                #Link to find trending topics
                tt =  "<input type=\"hidden\" name=\"qvalue\" value=" + query + "></input>\
                      <input type=\"hidden\" name=\"qtype\" value=" + type + "></input>\
                      <p><span id=\"trendingtopics\"></span><p><div id=\"wrapperfindtrendingtopics\"> \
                      <button type=\"button\" class=\"btn btn-default\"><a href=\"javascript:void();\" id=\"findtrendingtopics\">Find trending topics</a></button></div></p>"
        elif (type == "contributor"):
                sh = "<p class=\"tpadding text-success\">" + "Repositories " + query + " has contributed to (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>"
        elif (type == "language"):
                sh = "<p class=\"tpadding text-success\">Repositories written in " + query + " (processing time " + str(MyMoment.HTM(QST,"")).strip() +")</p>"            
        return ( total, tt + sh + "<ul class=\"list-group\">" + output + "</ul>")
    else:
        return (total, "EMPTY")  #0 rows return


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
    path2 = "&amp;action=Search\"  class=\"repositoryinfo\">"
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
        tmp3 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors</span>" if ( int(row['authors']) > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-user fa-1x\"></i>" + "1 contributor</span>"
        tmp4 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-home fa-1x\"></i>" + str(row['organization']) + "</span>" if ('organization' in row.keys()) else "" 
        tmp5 = "<sup><i class=\"rpadding fa fa-bullhorn fa-1x\">New</i></sup>" if ('CreateEvent' in row['type']) else "" 
        output += LIS + SB5 + path1 + row['full_name'].encode('utf-8').strip() + path2 + row['full_name'].encode('utf-8').strip() + path3 + tmp5 + DE + SB7 + tmp0 + tmp1 + tmp2 + tmp3  + tmp4 + DE + LIE
            
    return ( sh + ULS + output  + ULE)

def ReportTopOrganizations(heading):
    sh = "<h2 class=\"text-success\">" + heading + "</h2>"
    path1 = "<a href=\"/?q=organization "
    path2 = "&amp;action=Search\"  class=\"repositoryinfo\">"
    path3 = "</a>"
    output =""
    t2 = "class=\"list-group-item\""
    pipeline= [
               { '$match': {"type": {"$in": ["PushEvent"]}}},
               { "$group": {"_id": {"organization": "$organization"},"authoremails":{"$addToSet":"$actoremail"},"repositories":{"$addToSet":"$full_name"}}},
            #{"total": {"$add": ["$_id.rnum","$_id.authors"]}} 
               { "$project": {"_id":0,"organization":"$_id.organization","rnum":{"$size":"$repositories"},"authors":{"$size":"$authoremails"} }},
               { '$sort' : { 'authors': -1 }},
               { "$limit": DefaultLimit} 
               ]
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    for row in mycursor["result"]:
        if row['organization']:
            tmp1 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-users fa-1x\"></i>" + str(row['authors']) + " contributors</span>" if ( int(row['authors']) > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-user fa-1x\"></i>" + "1 contributor</span>"
            tmp2 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-file-code-o fa-1x\"></i>" + str(row['rnum']) + " repositories</span>" if ( int(row['rnum']) > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-file-code-o fa-1x\"></i>" + "1 repository</span>"
            output += LIS + SB5 + path1 + row['organization'] + path2 + row['organization'] + path3 + DE + SB7 + tmp1 + tmp2  + DE + LIE
            
    return ( sh + ULS + output  + ULE)

def ReportTopContributors(heading):
    myLimit = 18
    sh = "<h2 class=\"text-success\">" + heading + "</h2>"
    path1 = "<a href=\"/?q=contributor "
    path2 = "&amp;action=Search\"  class=\"repositoryinfo\">"
    path3 = "</a>"
    output =""
    t2 = "class=\"list-group-item\""
    pipeline= [
               { '$match': {"type": {"$in": ["PushEvent"]}}},
               { "$group": {"_id": {"actoremail": "$actoremail","actorname": "$actorname"},"organizations":{"$addToSet":"$organization"},"repositories":{"$addToSet":"$full_name"}}},
               # total = sum of repositories + sum of organizations x 10 
               { "$project": {"_id":1,"actoremail":"$_id.actoremail","actorname":"$_id.actorname","rnum":{"$size":"$repositories"},"onum":{"$size":"$organizations"},"total":{"$add":[{"$size":"$repositories"}, {"$multiply":[10,{"$size":"$organizations"}]}]}}},
               { '$sort' : { 'total': -1 }},
               { "$limit": myLimit} 
               ]
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    for row in mycursor["result"]:
        if row['actoremail']:
            tmp1 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-file-code-o fa-1x\"></i>" + str(row['rnum']) + " repositories</span>" if ( int(row['rnum']) > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-file-code-o fa-1x\"></i>" + "1 repository</span>"
            tmp2 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-home fa-1x\"></i>" + str(row['onum']) + " organizations</span>" if ( int(row['onum']) > 1) else "<span class=\"nobr\"><i class=\"lrpadding fa fa-home fa-1x\"></i>" + "1 organization</span>"
            output += LIS + SB5 + path1 + row['actoremail'] + path2 + row['actorname'] + path3 + DE + SB7 + tmp1 + tmp2  + DE + LIE
            
    return ( sh + ULS + output  + ULE)

def ReportTopLanguages(heading):
    myLimit = 15
    path1 = "<a href=\"/?q=language "
    path2 = "&amp;action=Search\"  class=\"repositoryinfo\">"
    path3 = "</a>"
    output = ""
    sh = "<h2 class=\"text-success\">" + heading + "</h2>" 
    pipeline= [
                { "$match": {"type": 'RepoInfo2'}},
                { "$unwind" : "$language" }, 
                { "$group": {"_id": {"language": "$language.l"},"lcount": {"$sum": 1}, "bcount": {"$sum": "$language.b"} }},
                { "$project": {"_id":1,"language":"$_id.language","lcount":"$lcount","bcount":"$bcount","total":{"$multiply": ["$lcount","$bcount"]}}},           
                { '$sort': {'lcount': -1}},
                { '$limit': myLimit}       
               ]    
    mycursor = db.aggregate(pipeline)

    for row in mycursor["result"]:
        tmp1 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-file-code-o fa-1x\"></i>" + numformat(row['lcount']) + " repositories</span>" 
        tmp2 = "<span class=\"nobr\"><i class=\"lrpadding fa fa-info fa-1x\"></i>" + numformat(row['bcount']) + " bytes</span>"
        output += LIS + SB5 + path1 + row['language'] + path2 + row['language'] + path3 + DE + SB7 + tmp1 + tmp2 + DE + LIE
            
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

  
def CommitFrequency ():
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
        else:
            range5 += record['frequency'] 
    
    output = LIS + SB12 + "<h3>Contributors commit frequency</h3><div class=\"chart-horiz clearfix\"><ul class=\"chart nlpadding\">" 
    output += "<li class=\"past\" title=\"1 commit\"><span class=\"bar\" data-number=\""+ str(range0) + "\"></span><span class=\"number\">"+ numformat(range0) + "</span></li>"
    output +="<li class=\"past\" title=\"2-3 commits\"><span class=\"bar\" data-number=\""+ str(range1) + "\"></span><span class=\"number\">"+ numformat(range1) + "</span></li>"
    output +="<li class=\"past\" title=\"4-5 commits\"><span class=\"bar\" data-number=\""+ str(range2) + "\"></span><span class=\"number\">"+ numformat(range2) + "</span></li>"
    output +="<li class=\"past\" title=\"6-10 commits\"><span class=\"bar\" data-number=\""+ str(range3) + "\"></span><span class=\"number\">"+ numformat(range3) + "</span></li>"
    output +="<li class=\"past\" title=\"11-15 commits\"><span class=\"bar\" data-number=\""+ str(range4) + "\"></span><span class=\"number\">"+ numformat(range4) + "</span></li>"
    output +="<li class=\"past\" title=\">15 commits\"><span class=\"bar\" data-number=\""+ str(range5) + "\"></span><span class=\"number\">"+ numformat(range5) + "</span></li>"
    output +="</ul></div>" +  DE + LIE    
    return output

def stringToDictionary(s, pairSeparator, keyValueSeparator):
    items = s.split(pairSeparator)
    data = {}
    for item in items:
        keyvalpair = item.split(keyValueSeparator)
        #Handle [u'message', u' Not Found']
        if (keyvalpair[1].strip() != 'Not Found'):
            data[keyvalpair[0].strip()] = int(keyvalpair[1].strip())
        else:
            break
    #print data
    #for (key, value) in data.items():
        #print key , "------->", value
    return data 

#Real-time dashboard
def Dashboard(type):
    t0 = TotalEntries("PushEvent",type)
    t1 = FindDistinct ('PushEvent','full_name','$full_name',type)
    t2=  FindDistinct ('CreateEvent','full_name','$full_name',type)
    t3 = FindDistinct ('PushEvent','actors','$actorlogin', type)
    t4 = FindDistinct ('PushEvent','organization','$organization', type)
    t5 = FindDistinct ('WatchEvent','full_name','$full_name', type)

    sh = "<h2 class=\"text-success\">Visual Dashboard</h2>"
    output0 =  LIS + SB12 + "<h2>" + numformat(t0) + " Commits</h2>"  + DE + LIE 
    output4 =  LIS + SB12 + "<h2>" + numformat(t5) + " Repositories Starred</h2>"  + DE + LIE
    
    #Repository, Contributors & Organizations
    output = LIS + SB12 + "<h3>Repositories, Contributors &amp; Organizations</h3><div class=\"chart-horiz clearfix\"><ul class=\"chart nlpadding\">" 
    output += "<li class=\"past\" title=\"Active Repositories\"><span class=\"bar\" data-number=\""+ str(t1)+ "\"></span><span class=\"number\">"+ numformat(t1) + "</span></li>"
    output += "<li class=\"past\" title=\"New Repositories\"><span class=\"bar\" data-number=\""+ str(t2)+ "\"></span><span class=\"number\">"+ numformat(t2) + "</span></li>"
    output += "<li class=\"past\" title=\"Contributors\"><span class=\"bar\" data-number=\""+ str(t3)+ "\"></span><span class=\"number\">"+ numformat(t3) + "</span></li>"
    output += "<li class=\"past\" title=\"Organizations\"><span class=\"bar\" data-number=\""+ str(t4)+ "\"></span><span class=\"number\">"+ numformat(t4) + "</span></li>"
    output += "</ul></div>" +  DE + LIE
    
    #Contributor commit frequency
    output3 = CommitFrequency()
    
    return (sh + ULS + output0 + output4 + output + output3 + ULE)
    
    
def LanguageBreakdown(RFNK):
    t1 = "Language" 
    RFN = bleach.clean(RFNK).strip()
    output = ""
    sum = 0 
    pipeline= [
                { "$match": {"type": 'RepoInfo2' ,'full_name': RFN}},     
                { "$group": {"_id": {"full_name": "$full_name","language":"$language"}}},
                { "$project": { '_id': 0, 'full_name': '$_id.full_name','language':'$_id.language'}}
               ]    
    mycursor = db.aggregate(pipeline)
    #print mycursor
    
    for row in mycursor["result"]:    
        d = {}
        for x in row['language']:
            d[x['l']] = x['b']            
        #for k, v in sorted(d.items(), key=lambda kv: kv[1], reverse=True):
        #    print("%s => %s" % (k,v))
        output += "<div class=\"chart-horiz clearfix\"><ul class=\"chart nlpadding\">"
        #Sum of bytes of code
        for (key, value) in d.items():
            sum += value
        #Find each language %    
        for k, v in sorted(d.items(), key=lambda kv: kv[1], reverse=True):
            percentage = int(round(v / (sum + 0.0)*100,2))
            #Group languages less than 10%
            if (percentage < 10.00):
                percentage = "<10"
                #Calculate 10% of total and group all languages less than 5%
                v = int(round(sum * 9.99/100))
            output += "<li class=\"past\" title=\"" + str(k) + "\"><span class=\"bar\" data-number=\""+ str(v)+ "\"></span><span class=\"number\">"+str(percentage) + "%" + "</span></li>"
        output+="</ul></div>"    
        if (len(output) > 0):
            if (output.count("past") > 1):
                t1 = "Languages" 
            return (LGIHS + t1 + LGIHE + "<ul class=\"nlpadding\">" + output + "</ul>") 
        else:
            return (LGIHS + t1 + LGIHE + "<span class=\"text-danger\">None</span>")
    
    #Handle use case - no languages stored yet!
    if (len(mycursor['result']) == 0):
        return (LGIHS + t1 + LGIHE + "<span class=\"text-danger\">You've got me stumped!</span>")
    
def CloseDB():
    connection.close()