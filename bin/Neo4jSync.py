from pymongo import MongoClient
import os.path, time, sys
from py2neo import neo4j,Graph,Node,Relationship
import os.path
import bleach
import re
import chardet
import string
import time

sys.path.append('../')
import MyMoment

#MongoDB & Neo4j connections
MONGO_URL = os.environ['connectURLRead']
connection = MongoClient(MONGO_URL)
db = connection.githublive.pushevent
graph = Graph(os.environ['neoURLProduction'])

def numformat(value):
    return "{:,}".format(value)

#Handle encoding
def HE(s):
	return s.encode('utf-8').strip()

#Sanitize email + Handle encoding
def SE(s):
	try:
	 	s.decode('ascii')
	except:
    	#print "it was not a ascii-encoded unicode string"
		return 0
	else:
		if len(s) > 1:
			if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", s) != None:
				return 1
			else:
				return 0
 		else:
 			return 0
 	
def Nodes(): 
	for record in graph.cypher.execute("match n return count(*) as count"):
		return numformat(record.count)
	
def Edges():
	for record in graph.cypher.execute("match (a)-[r]->(b) return count(r) as count"):
		return numformat(record.count)
	
	 		
def CNR():			
    #Find entries in the past 120 minutes
    since = MyMoment.TTEM(120)
    print MyMoment.MT() + " start: creating new nodes and relations since ", since
    print "#Nodes:", Nodes(), " #Relations:",Edges()
    pipeline=[
              {'$match': {'$and': [ {'sha': { '$exists': True }},{'created_at': { '$gt': since }} ]}},
              { '$group': {'_id': {'full_name': '$full_name','organization': '$organization' }, '_a1': {"$addToSet": "$actorlogin"}}},
              { '$project': { '_id': 0, 'full_name': "$_id.full_name", 'organization': "$_id.organization",'actorlogin': "$_a1"}},
              ]
    mycursor = db.aggregate(pipeline)
    t = 0
    for record in mycursor["result"]:
        print "processing ......",record["full_name"]    
        if "github.io" not in record["full_name"]:
            #print "adding node ......",record["full_name"]    
            r = graph.merge_one("Repository", "id", record["full_name"])
            r.properties["created_at"] = MyMoment.TNEM()
            r.push()   
            #Create organization
            if ('organization' in record.keys()):
                o = graph.merge_one("Organization", "id", record["organization"])
                o.properties["created_at"] = MyMoment.TNEM()
                o.push()
                #print "processing .... ", record["full_name"], "IN_ORGANIZATION", record["organization"] 
                rel = Relationship(r,"IN_ORGANIZATION",o)
                graph.create_unique(rel)
                t = t + 1        
            #Create actor relation
            for al in record['actorlogin']:
                #print "processing .... ", record["full_name"], "IS_ACTOR", al
                if (SE(al) == 1):
                    p = graph.merge_one("People", "id", al)
                    p.properties["created_at"] = MyMoment.TNEM()
                    p.push()
                    rel = Relationship(r,"IS_ACTOR",p)
                    graph.create_unique(rel)
                    t = t + 1
        #else:
            #print "ignore ...",record["full_name"] 
    print MyMoment.MT() + " end: generating new nodes and building new relations ...",t
    print "#Nodes:", Nodes(), " #Relations:",Edges()
    print "Deleting nodes and relations older than 24 hours ..."
    DayAgo =  MyMoment.TTEM(60*24)
    d1 = "MATCH (a)-[r]-() where a.created_at <" + str(DayAgo) + " delete a,r"
    d2 = "MATCH (a) where a.created_at <" + str(DayAgo) + " delete a"
    graph.cypher.execute(d1)
    graph.cypher.execute(d2)
    print "#Nodes:", Nodes(), " #Relations:",Edges()
     
	
#Create Nodes & Relations
CNR()
