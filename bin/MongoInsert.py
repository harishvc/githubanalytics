from py2neo import Graph
import os.path
from flask import Flask
app = Flask(__name__)
from pymongo import MongoClient


#TODO: delete document before entry

graph = Graph(os.environ['neoURL'])
MONGO_URL = os.environ['connectURL']
connection = MongoClient(MONGO_URL)
db = connection.githublive.pusheventCapped

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
 		#Delete old entry
 		#db.remove({'type':'similarrepositories','url': Inputrepo})
 		
 		#Insert to MongoDB
 		mongo_record_insert = {'type': 'similarrepositories', 'url': Inputrepo, 'similar': outputString}
 		db.insert(mongo_record_insert)
 

def FindAllRepositories():
	query = "MATCH (n:`Repository`) RETURN n.url as url"
	result = graph.cypher.execute(query)
	for entries in result: 
		print "Processing ..... ", entries.url
		SimilarRepositories(entries.url)
		

FindAllRepositories()
		