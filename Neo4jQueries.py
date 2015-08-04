from py2neo import authenticate, Graph
import os.path
import bleach
from flask import Flask
app = Flask(__name__)

def FindSimilarRepositories(InputrepoK):
	#Sanitize input
	Inputrepo = bleach.clean(InputrepoK).strip()
	host  = os.environ['LOCALNEO4JIPPORT']
	login = os.environ['LOCALNEO4JLOGIN']
	password = os.environ['LOCALNEO4JPASSWORD']
	authenticate(host,login,password)
	graph = Graph(os.environ['neoURLlocal'])
	output = ""
	path1 = "<a href=\"/?q=repository "
	path2 = "&amp;action=Search\"  class=\"repositoryinfo\">"
	path3 = "</a>"

    #Find similar repository > 1 connections
	query1="MATCH (a {id:\"" + Inputrepo + "\"})"
	query2="-[r1:IS_ACTOR|IN_ORGANIZATION]->(match)<-[r2:IS_ACTOR|IN_ORGANIZATION]-(b) "
	query3="with b, collect (distinct match.id) as connections, collect (distinct type(r1)) as rel1 "
	query4="where length(connections) >= 1 return b.id,length(connections) as count,length(rel1) as rel "
	query5="order by length(connections)  desc limit 5" 
	
	query = query1 + query2 + query3 + query4 + query5 
	#print query
	
	a = graph.cypher.execute(query)
	for record in a:
		if (record['rel'] < 2):
   		 	output += "<li>" + path1 + record['b.id'] + path2 + record['b.id'] + path3 + ": " + str(record['count']) + " contributors in common</li>"
   		else:
   			output += "<li>" + path1 + record['b.id'] + path2 + record['b.id'] + path3 + ": " + str(record['count']-1) + " contributors in common &amp; belong to same organization</li>"
 	if (len(output) > 0):
 		return ("<ul>" + output + "</ul>") 
 	else:
 		#Nothing found!
   		return "<span class=\"text-danger\">You got me stumped!</span>"

