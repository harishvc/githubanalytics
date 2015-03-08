from py2neo import Graph
import os.path
from flask import Flask
app = Flask(__name__)

def FindSimilarRepositories(Inputrepo):
	graph = Graph(os.environ['neoURLProduction'])
	output = ""
	path1 = "<a href=\"/?q=repository "
	path2 = "&amp;action=Search\">"
	path3 = "</a>"

    #Find similar repository > 3 connections       
	query1= """MATCH (a)-[r1:IS_ACTOR|IN_ORGANIZATION]->(match)<-[r2:IS_ACTOR|IN_ORGANIZATION]-(b)  where a <> b and """
	query2="a.id = " + "\"" + Inputrepo + "\" " 
	query3="""with b, collect (distinct match.id) as connections, collect (distinct type(r1)) as rel1 
            where length(connections) >= 3
            return b.id,length(connections) as count,length(rel1) as rel order by length(connections)  desc limit 5""" 
	
	query = query1 + query2 + query3  
	a = graph.cypher.execute(query)
	for record in a:
		if (record['rel'] < 2):
   		 	output += "<li>" + path1 + record['b.id'] + path2 + record['b.id'] + path3 + ": " + str(record['count']) + " contributors in common</li>"
   		else:
   			output += "<li>" + path1 + record['b.id'] + path2 + record['b.id'] + path3 + ": " + str(record['count']-1) + " contributors in common &amp; belong to same organization</li>"
 	if (len(output) > 0):
 		return ("<ul>" + output + "</ul>") 
 	else:
   		return output

