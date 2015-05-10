#Source: http://neo4j.com/blog/neo4j-building-topic-graph-prismatic-interest-graph-api/
#Reference: https://github.com/Prismatic/interest-graph#topic-tagging

from pymongo import MongoClient
import time
import requests
import json
import os
import re

#Configure for production or development based on environment variables
if (os.environ['deployEnv'] == "production"):
    MONGO_URL = os.environ['connectURLRead']
    connection = MongoClient(MONGO_URL)
    db = connection.githublive.pushevent
else: 
    MONGO_URL = os.environ['connectURLReaddev']
    connection = MongoClient(MONGO_URL)
    db = connection.githubdev.pushevent
        
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate
 
@RateLimited(0.3)
def topics(body):
    payload = { 
                'body': body,
                'api-token': os.environ['prismatickey']} 
    return (requests.post("http://interest-graph.getprismatic.com/text/topic", data=payload))

def GetInterestTopics(type,value):
    pipeline = [
                    {'$match':{'$and':[{'type':{'$in':["PushEvent"]}},{type:value}]}}, 
                    {'$group':{'_id':{type:value},'comments':{"$addToSet":"$comment"}}} 
                ]
    mycursor = db.aggregate(pipeline)
    #print mycursor
    P1 = ""
    P2 = ""
    rt = []  #returned topics
    output = "<p class=\"tpadding text-success\">" + "Trending topic(s) in organization " + value + "</p>"
    for row in mycursor["result"]: 
        P1 = ''.join(row['comments']) 
        #clean up: remove spaces
        #TODO: remove special characters, html, +++ , ====
        P2 = re.sub( '\s+', ' ', P1).strip()
    #Condition 1: Call Prismatic API when there is more than 500 characters in comments    
    if len(P2) > 500:
        P3 = ""
        #Condition 2: Send only 2k characters
        P3 = topics(P2[0:20000]).json()
        #Condition 3: Handle no topic return 
        if len(P3['topics']) > 0:
            for topic in P3['topics']:
                rt.append(topic['topic'])
            if len(rt) > 1:
                output = "<p class=\"tpadding text-success\">Interesting topics</p>"
            else:
                output = "<p class=\"tpadding text-success\">Interesting topic</p>"
            output += ', '.join(rt)     
        else:
            output = "<p class=\"tpadding text-success\">Sorry, found no topic based on contributor comment(s)</p>"
    else:
        output = "<p class=\"tpadding text-success\">Sorry, no topic found based on contributor comment(s)</p>"
    return output
    