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
CSVPUBLICDIR = os.environ['CSVPUBLICDIR']
CSVPUBLICURL = os.environ['CSVPUBLICURL']

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
 			return 
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
    
def CC():	
    graph.cypher.execute("CREATE CONSTRAINT ON (a:Repository) ASSERT a.id IS UNIQUE")
    graph.cypher.execute("CREATE CONSTRAINT ON (b:People) ASSERT b.id IS UNIQUE")
    graph.cypher.execute("CREATE CONSTRAINT ON (c:Organization) ASSERT c.id IS UNIQUE")
 		
def GenerateCSV():			
    #Find entries in the past  1 hour 15 minutes (GitHub Events are processed hourly at 15 minutes past the hour)
    since = MyMoment.TTEM(75)
    print MyMoment.MT() + " start: mongodb documents since ", since
    pipeline=[
              {'$match': {'$and': [ {'sha': { '$exists': True }},{'created_at': { '$gt': since }}, {"full_name" : {'$nin': [re.compile('.*github.io.*'),re.compile('.*github.com.*')]} }]}},
              { '$group': {'_id': {'full_name': '$full_name','organization': '$organization' }, '_a1': {"$addToSet": "$actorlogin"}}},
              { '$project': { '_id': 0, 'full_name': "$_id.full_name", 'organization': "$_id.organization",'actorlogin': "$_a1"}}
              ]
    mycursor = db.aggregate(pipeline)
    print MyMoment.MT() + ": #new mongodb documents found .... " +  str(len(mycursor['result']))
    sys.stdout.flush()
    file1 = open(CSVPUBLICDIR + "/repositories.csv", 'w+')
    file2 = open(CSVPUBLICDIR + "/organizations.csv", 'w+')
    file4 = open(CSVPUBLICDIR + "/inorganization-relations.csv", 'w+')
    file3 = open(CSVPUBLICDIR + "/people.csv", 'w+')
    file5 = open(CSVPUBLICDIR + "/isactor-relations.csv", 'w+')
    file1.write("id|now\n")
    file2.write("id|now\n")
    file3.write("id|now\n")
    file4.write("a|b\n")
    file5.write("a|b\n")
    print MyMoment.MT() +  ": start generating CSV files"
    for record in mycursor["result"]:
        #print "processing ... ", record["full_name"]
        file1.write(record["full_name"] + "|" + str(MyMoment.TNEM()) + "\n")
        if ('organization' in record.keys()):
            file2.write(record["organization"] + "|" + str(MyMoment.TNEM()) + "\n")
            file4.write(record["full_name"] + "|" + record["organization"] + "\n")
        for al in record['actorlogin']:
            if (SE(al) == 1):
                 file3.write(al + "|" + str(MyMoment.TNEM()) + "\n")
                 file5.write(record["full_name"] + "|" + al + "\n")
    print MyMoment.MT() +  ": end generating CSV files"
    file1.close()
    file2.close()
    file3.close()
    file4.close()
    file5.close()
    
def LoadCSV():
    #Small batch    
    PC = "USING PERIODIC COMMIT 100\n"
    r1 = "LOAD CSV WITH HEADERS FROM \"" + CSVPUBLICURL + "/repositories.csv\" AS csvLine FIELDTERMINATOR \"|\""   
    r2 =  " MERGE (r:Repository {id: csvLine.id}) "
    r3 =  " SET r.created_at = toInt(csvLine.now)"
    print MyMoment.MT() +  ": start processing repositories.csv ....."
    graph.cypher.execute(PC + r1 + r2 + r3)
    print MyMoment.MT() + ": end processing repositories.csv"    
    o1 = "LOAD CSV WITH HEADERS FROM \"" + CSVPUBLICURL + "/organizations.csv\" AS csvLine FIELDTERMINATOR \"|\""   
    o2 =  " MERGE (o:Organization {id: csvLine.id}) "
    o3 =  " SET o.created_at = toInt(csvLine.now)"
    print MyMoment.MT() + ": start processing organizations.csv ....."
    graph.cypher.execute(PC + o1 + o2 + o3)
    print MyMoment.MT() + ": end processing organizations.csv"    
    z1 = "LOAD CSV WITH HEADERS FROM \"" + CSVPUBLICURL + "/inorganization-relations.csv\" AS csvLine FIELDTERMINATOR \"|\""   
    z2 = " MATCH (a:Repository { id: csvLine.a}),(b:Organization {id: csvLine.b}) "
    z3 = " CREATE UNIQUE (a)-[:IN_ORGANIZATION]->(b)" 
    print MyMoment.MT() + ": start processing inorganization-relations.csv ....."
    graph.cypher.execute(PC + z1 + z2 + z3)
    print MyMoment.MT() + ": end processing inorganization-relations.csv"
    p1 = "LOAD CSV WITH HEADERS FROM \"" + CSVPUBLICURL + "/people.csv\" AS csvLine FIELDTERMINATOR \"|\""   
    p2 =  " MERGE (o:People {id: csvLine.id}) "
    p3 =  " SET o.created_at = toInt(csvLine.now)"
    print MyMoment.MT() + ": start processing people.csv ....."
    graph.cypher.execute(PC + p1 + p2 + p3)
    print MyMoment.MT() + ": end processing people.csv"    
    z1 = "LOAD CSV WITH HEADERS FROM \"" + CSVPUBLICURL + "/isactor-relations.csv\" AS csvLine FIELDTERMINATOR \"|\""   
    z2 = " MATCH (a:Repository { id: csvLine.a}),(b:People {id: csvLine.b}) "
    z3 = " CREATE UNIQUE (a)-[:IS_ACTOR]->(b)" 
    print MyMoment.MT() + ": start processing isactor-relations.csv ....."
    graph.cypher.execute(PC + z1 + z2 + z3)
    print MyMoment.MT() + ": end processing isaction-relations.csv"    

def Cleanup():
    print MyMoment.MT() + ": #Nodes:", Nodes(), " #Relations:",Edges()    
    print MyMoment.MT() + ": Deleting nodes and relations older than 28 hours ..."
    DayAgo =  MyMoment.TTEM(60*28)
    d1 = "MATCH (a)-[r]-() where toInt(a.created_at) <" + str(DayAgo) + " delete a,r"
    d2 = "MATCH (a) where toInt(a.created_at) <" + str(DayAgo) + " delete a"
    graph.cypher.execute(d1)
    graph.cypher.execute(d2)
    print MyMoment.MT() + ": #Nodes:", Nodes(), " #Relations:",Edges()    

#Create constraints & index
CC()        
#Generate CSV files with nodes & relations
GenerateCSV()
print MyMoment.MT() + ": #Nodes:", Nodes(), " #Relations:",Edges() 
print MyMoment.MT() + ": start inserting ....."
#Load CSV files
LoadCSV()
print MyMoment.MT() + ": end inserting"

#Delete old nodes and relationss
Cleanup()


