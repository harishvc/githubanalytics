from pymongo import MongoClient
import os.path, time, sys
from py2neo import neo4j,Graph,Node,Relationship,batch,rewrite,watch
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

#Determine Nodes and breakdown 	
def Nodes(): 
    for record in graph.cypher.execute("match n return count(n) as count"):
        total = numformat(record.count)
    for record in graph.cypher.execute("match (a:Repository) return count(a) as count"):    
        r = numformat(record.count)
    for record in graph.cypher.execute("match (a:People) return count(a) as count"):    
        a = numformat(record.count)
    for record in graph.cypher.execute("match (a:Organization) return count(a) as count"):    
        o = numformat(record.count)
    output = "Nodes:" + str(total) + " (" + "Repositories:" + str(r) + " People:" + str(a) + " Organization:" + str(o) + ")"        
    return output

#Determine edges and breakdown    
def Edges():
    for record in graph.cypher.execute("match (a)-[r]->(b) return count(r) as count"):
        total = numformat(record.count)
    for record in graph.cypher.execute("match (a:Repository)-[r]->(b:People) return count(r) as count"):
        RA = numformat(record.count)
    for record in graph.cypher.execute("match (a:Repository)-[r]->(b:Organization) return count(r) as count"):
        RO = numformat(record.count)
    output = "Relations:" + str(total) + " (" + "Repositories->People:" + str(RA) + ", Repositories->Organization:" + str(RO) + ")"        
    return output
    
	 		
def CNR():			
    #Find entries in the past  2 hours 15 minutes (GitHub Events are processed hourly at 15 minutes past the hour)
    since = MyMoment.TTEM(135)
    print MyMoment.MT() + " start: creating new nodes and relations since ", since
    #Force Python's print function
    sys.stdout.flush()
    print Nodes(),Edges()
    sys.stdout.flush()
    pipeline=[
              {'$match': {'$and': [ {'sha': { '$exists': True }},{'created_at': { '$gt': since }}, {"full_name" : {'$nin': [re.compile('.*github.io.*'),re.compile('.*github.com.*')]} }]}},
              { '$group': {'_id': {'full_name': '$full_name','organization': '$organization' }, '_a1': {"$addToSet": "$actorlogin"}}},
              { '$project': { '_id': 0, 'full_name': "$_id.full_name", 'organization': "$_id.organization",'actorlogin': "$_a1"}}
              #{ '$sort' : { 'full_name': -1 }}
              #{ '$limit': 5}
              ]
    mycursor = db.aggregate(pipeline)
    count = 0
    batch = 0
    #https://github.com/nigelsmall/py2neo/issues/361
    rewrite(("http", "localhost", 0), ("https", os.environ['neoURLProductionURI'], os.environ['neoURLProductionPort'])) 
    tx = graph.cypher.begin()
    print MyMoment.MT() + ": #entries to process .... " +  str(len(mycursor['result']))
    sys.stdout.flush()
    for record in mycursor["result"]:
        #print "processing ......",record["full_name"]
        count = count + 1    
        statement1 = "MERGE (r:Repository {id:{ID}}) RETURN r"
        tx.append(statement1,{"ID":record["full_name"]})                   
        statement2 = "MATCH (r { id: {ID} }) SET r.created_at = {TN} RETURN r"
        tx.append(statement2,{"ID":record["full_name"],"TN":MyMoment.TNEM()}) 
        #Create organization
        if ('organization' in record.keys()):
            statement3 = "MERGE (o:Organization {id:{ID}}) RETURN o"
            tx.append(statement3,{"ID":record["organization"]})  
            statement4 = "MATCH (o { id: {ID} }) SET o.created_at = {TN} RETURN o"
            tx.append(statement4,{"ID":record["organization"],"TN":MyMoment.TNEM()})
            #print "creating IN_ORGANIZATION ...."
            statement5 = "MATCH (o:Organization), (r:Repository) WHERE o.id = {oID} and r.id ={rID} CREATE UNIQUE (r)-[:IN_ORGANIZATION]->(o)"
            tx.append(statement5,{"rID":record["full_name"],"oID":record["organization"]})
        #Create actor relation
        for al in record['actorlogin']:
            if (SE(al) == 1):
                statement6 = "MERGE (p:People {id:{ID}}) RETURN p"
                tx.append(statement6,{"ID":al})      
                statement7 = "MATCH (p { id: {ID} }) SET p.created_at = {TN} RETURN p"
                tx.append(statement7,{"ID":al,"TN":MyMoment.TNEM()})    
                statement8 = "MATCH (p:People), (r:Repository) WHERE p.id = {pID} and r.id ={rID} CREATE UNIQUE (r)-[:IS_ACTOR]->(p)"
                tx.append(statement8,{"rID":record["full_name"],"pID":al})
        #Start processing in small batches
        if (count > 25):
            #Keep going!!!
            batch = batch + 1
            print MyMoment.MT() + ": start batch ... " + str(batch)
            sys.stdout.flush()
            count = 0
            tx.process()

    print MyMoment.MT() + ": start commit transactions ...."
    sys.stdout.flush()
    tx.commit()
    print MyMoment.MT() + ": end commit transactions ....."
    sys.stdout.flush()
    print MyMoment.MT() + " end: generating new nodes and building new relations ..."
    print MyMoment.MT() + ": #Nodes:", Nodes(), " #Relations:",Edges()
    print MyMoment.MT() + ": Deleting nodes and relations older than 24 hours ..."
    DayAgo =  MyMoment.TTEM(60*24)
    d1 = "MATCH (a)-[r]-() where a.created_at <" + str(DayAgo) + " delete a,r"
    d2 = "MATCH (a) where a.created_at <" + str(DayAgo) + " delete a"
    graph.cypher.execute(d1)
    graph.cypher.execute(d2)
    print MyMoment.MT() + ": #Nodes:", Nodes(), " #Relations:",Edges()
 
	
#Create Nodes & Relations
CNR()
