from py2neo import Graph
import os.path,  sys
from flask import Flask
app = Flask(__name__)
from pymongo import MongoClient
import json
import re
import cgi


#Local Module
sys.path.append('../')
import MyMoment

#Global variables
TSR = {}
TSR["type"] =  "similarrepositories"

#DB connections
graph = Graph(os.environ['neoURL'])
MONGO_URL = os.environ['connectURL']
connection = MongoClient(MONGO_URL)
db = connection.githublive.pushevent
		
#Create queries for MongoDB insert
MONGODBFILE="mongodb-" + MyMoment.FT() + ".txt"
#MONGODBFILE="mongodb-17Jan2015-160635.txt"

#Write to external file for batch process
f = open(MONGODBFILE,"w")
#f = open(MONGODBFILE,"r")

def SimilarRepositories(Inputrepo):
	output = []
	outputString =""
	mongo_record_insert = {}
	path1 = "<a href=\"/?q=repository "
	path2 = "&amp;action=Search\">"
	path3 = "</a>"
	query1= """MATCH (me)-[r1:IS_LANGUAGE|IS_OWNER|IN_ORGANIZATION|IS_ACTOR]->(stuff)<-[r2:IS_LANGUAGE|IS_OWNER|IN_ORGANIZATION|IS_ACTOR]-(repo) """
	query2="WHERE me.url = " + "\"" + Inputrepo + "\"" 
	query3=""" AND type (r1) = type (r2)
        	   RETURN repo.name as reponame, repo.url as url, count(stuff) as count                
           	   ORDER BY count(stuff) DESC LIMIT 5"""               
	query = query1 + query2 + query3  
	result = graph.cypher.execute(query)
	for entries in result: 
		output.append(path1 + entries.url.encode('utf-8').strip() + path2 + entries.reponame.encode('utf-8').strip() + path3)                        

			 
 	if len(output) !=0 : 
 		outputString +=  ", ".join(output)
 		#Escape 		
		tmp1 = outputString.replace('"','\\"')
		tmp2 = cgi.escape(tmp1)
		f.write('\'type\'' + ':' + '\'similarrepositories\'' + ',' + '\'url\'' + ':' +  '\'' + Inputrepo + '\',' + '\'similar\'' + ':\'' +  tmp2 + '\'' + "\n")          
 	

def FindAllRepositories():
	print MyMoment.MT(), "start: generating similar repositories ..." , MONGODBFILE
	query = "MATCH (n:`Repository`) RETURN n.url as url"
	result = graph.cypher.execute(query)
	for entries in result: 
		#print "Processing ..... ", entries.url
		SimilarRepositories(entries.url)
  	print MyMoment.MT(), "end: generating similar repositories ..." , MONGODBFILE  
  	f.close()
		

def Insert2Mongo():
	if (os.path.exists(MONGODBFILE)):		
		#Delete old entries
		print MyMoment.MT(), "start: deleting old similar repositories inside mongodb ..."
		db.remove(TSR,safe=True)
		print MyMoment.MT(), "end: deleting old similar repositories inside mongodb ..."
		#Process line by line
		print MyMoment.MT(), "start: inserting similar repositories inside mongodb ..."
		#Bulk insert
		bulk = db.initialize_unordered_bulk_op()
		d = {}
		ctr = 0
		with open(MONGODBFILE) as f:
			for line in f.readlines():
				ctr = ctr + 1 
				s = "{" + line + "}"
				json_acceptable_string = s.replace("'", "\"")
				d = json.loads(json_acceptable_string)
				bulk.insert(d)
		#Batch execute        
		bulk.execute()
		print MyMoment.MT(), "end: inserting similar repositories inside mongodb ... inserted " , ctr
		#Archive queries
		destination = "./ARCHIVE/" + MONGODBFILE
		os.rename(MONGODBFILE, destination)
	else:
		print MyMoment.MT(), "error:", MONGODBFILE, " does not exist"

	
FindAllRepositories()
Insert2Mongo()		