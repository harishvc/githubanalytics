from pymongo import MongoClient
import os.path, time, sys
from py2neo import Graph
import os.path
import bleach
import re
import chardet
import string

#Local Module
sys.path.append('../')
import MyMoment

#References
#http://jexp.de/blog/2014/06/load-csv-into-neo4j-quickly-and-successfully/
#http://neo4j.com/docs/stable/cypherdoc-create-nodes-and-relationships.html


#Create file name based on timestamp
CYPHERFILE="cypher-" + MyMoment.FT() + ".txt"
OUTPUTFILE= "./output.txt"

#Handle encoding
def HE(s):
	return s.encode('utf-8').strip()

#Sanitize email + Handle encoding
def SE(s):
	#return s.decode('utf-8').strip().replace('\'','').replace('\"','')
    #return bleach.clean(s).strip()
    #return s.decode('unicode_escape')

	#for c in s:
	#	if c not in string.ascii_letters:
	#		return 0
	#if len(s) > 1:
	#	if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", s) != None:
	#		return 1
	#return 0


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
 		
def CreateCypher():
		
	#MongoDB connections
	MONGO_URL = os.environ['connectURLRead']
	connection = MongoClient(MONGO_URL)
	db = connection.githublive.pushevent
	
    #Create new file to holde cypher queries
	f = open(CYPHERFILE,"w")
	f2 = open(OUTPUTFILE,"a") #output + errors
	
	f2.write(MyMoment.MT() + " start: generating new nodes and building new relations ..." + CYPHERFILE + "\n")

	#Delete old entries inside Neo4j
	f.write("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r;\n")
     
	#Generate unique repositories
	pipeline= [
           { '$match': {'sha': { '$exists': True }}},    
           { '$group': { '_id': {'url': '$url',  'name': '$name', 'full_name': '$full_name'}}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'name': '$_id.name' ,'full_name': '$_id.full_name'} },
           ]
	mycursor = db.aggregate(pipeline)
	rctr = 0	
	for record in mycursor["result"]:
		rctr = rctr + 1
		f.write("CREATE (r" + str(rctr) + ":Repository {id:\'" + HE(record['full_name']) + "\', name:\'" + HE(record['name']) + "\', url:\'" + HE(record['url']) + "\'});\n")


	#Generate unique languages
	#pipeline= [
    #       { '$match': {'sha': { '$exists': True }}},    
    #       { '$group': { '_id': {'language': '$language'}}},
    #       { '$project': { '_id': 0, 'language': '$_id.language'}},
    #       ]
	#mycursor = db.aggregate(pipeline)	
	#lctr = 0
	#for record in mycursor["result"]:
	#	lctr = lctr + 1
	#	n = str(record['language'])
	#	f.write("CREATE (l" + str(lctr) + ":Language {id:\'" + str(record['language']) + "\', name:\'" + str(record['language']) + "\'});\n")

 
	#Generate unique people
	pipeline= [
           { '$match': {'sha': { '$exists': True }}},    
           { '$group': { '_id': {'actorlogin': '$actorlogin',  'actorname': '$actorname'}}},
           { '$project': { '_id': 0, 'actorlogin': '$_id.actorlogin', 'actorname': '$_id.actorname'}},
           ]
	mycursor = db.aggregate(pipeline)	
	pctr = 0
	for record in mycursor["result"]:
		pctr = pctr + 1
		f.write("CREATE (p" + str(pctr) + ":People {id:\'" + HE(record['actorlogin']) + "\', name:\'" + HE(record['actorname']).replace('\'','').replace('\\','') + "\', login:\'" + HE(record['actorlogin']) + "\'});\n")

	#Generate unique organizations
	pipeline= [
           { '$match': {'sha': { '$exists': True }}},    
           { '$group': { '_id': {'organization': '$organization'}}},
           { '$project': { '_id': 0, 'organization': '$_id.organization'}},
           ]
	mycursor = db.aggregate(pipeline)
	octr = 0	
	for record in mycursor["result"]:
		octr = octr + 1
		f.write("CREATE (o" + str(octr) + ":Organization {id:\'" + str(record['organization']) + "\', name:\'" + str(record['organization']) + "\'});\n")


    #Find relations for each repository
	pipeline= [
		   { '$match': {'sha': { '$exists': True }}}, 
		   { '$group': {'_id': {'url': '$url',  'full_name': '$full_name','organization': '$organization' }, '_a1': {"$addToSet": "$actorlogin"}}},
		   { '$project': { '_id': 0, 'full_name': "$_id.full_name", 'organization': "$_id.organization",'actorlogin': "$_a1"}},
		   ]
	mycursor = db.aggregate(pipeline)	
	for record in mycursor["result"]:
		ri =  record['full_name']
        #Create language relation
		#for lang in record['language']:
			#Ignore commits with "null" language
			#if ( lang != None):
				#f.write("MATCH (a:Repository {id:\'" + ri + "\'}) MATCH (b:Language {id:\'" + lang +"\'}) CREATE (a)-[:IS_LANGUAGE]->(b);\n")
		
		#Create actor relation
		for al in record['actorlogin']:
			#print "processing .... ", al
			if (SE(al) == 1):
				#print "->",ri,"<-  ->", SE(al), "<-"
				f.write("MATCH (a:Repository {id:\'" + ri + "\'}) MATCH (b:People {id:\'" + al +"\'}) CREATE (a)-[:IS_ACTOR]->(b);\n")
			#else:
				#print "ignoring ....." , al
				#f2.write("ignoring ........ " + HE(al) + "\n")
				
				
		#create organization & owner relation
		if ('organization' in record):
			f.write("MATCH (a:Repository {id:\'" + ri + "\'}) MATCH (b:Organization {id:\'" + HE(record['organization']) +"\'}) CREATE (a)-[:IN_ORGANIZATION]->(b);\n")
		#else:
			#f.write("MATCH (a:Repository {id:\'" + ri + "\'}) MATCH (b:People {id:\'" + HE(record['owner']) +"\'}) CREATE (a)-[:IS_OWNER]->(b);\n")
			
			
	f2.write(MyMoment.MT() + " end: generating new nodes and building new relations ..." + CYPHERFILE + "\n")
	
 	#close file handle
 	f.close()
 	f2.close()
    
    
def InsertCypher():
	if (os.path.exists(CYPHERFILE)):
		graph = Graph(os.environ['neoURLProduction'])
		#Read Cypher and process line by line
		print MyMoment.MT(), "start: inserting new nodes and building new relations ..."
		with open(CYPHERFILE) as f:
			for line in f.readlines():
				graph.cypher.execute(line)
		print MyMoment.MT(), "end: inserting new nodes and building new relations ..."
		#Archive Cypher
		destination = "./ARCHIVE/" + CYPHERFILE
		os.rename(CYPHERFILE, destination)
	else:
		print MyMoment.MT(), "error:", CYPHERFILE, " does not exist"

      
#Generate Cypher queries from Mongodb      
CreateCypher()
#Insert Cypher queries inside neo4j
#InsertCypher()
