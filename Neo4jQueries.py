from py2neo import Graph
import os.path
from flask import Flask
app = Flask(__name__)

#TODO: app.debug not working
#TODO: Generate query
#TODO: Generate reply

def FindSimilarRepositories(Inputrepo):
	graph = Graph(os.environ['neoURL'])
	output = []
	outputString =""
	query1= """MATCH (me)-[r1:IS_LANGUAGE|IS_OWNER|IN_ORGANIZATION|IS_ACTOR]->(stuff)<-[r2:IS_LANGUAGE|IS_OWNER|IN_ORGANIZATION|IS_ACTOR]-(repo) """
	query2="WHERE me.url = " + "\"" + Inputrepo + "\"" 
	query3=""" AND type (r1) = type (r2)
        	   RETURN repo.name as reponame, repo.url as url, count(stuff) as count                
           	   ORDER BY count(stuff) DESC LIMIT 5"""               
	query = query1 + query2 + query3  
	result = graph.cypher.execute(query)
        app.logger.debug ("# Similar repositories:", len(result))

	for entries in result: 
        	#print entries.reponame, entries.url, entries.count
        	#output.append("<a href=" + entries.url.encode('utf-8').strip() + ">" + entries.reponame.encode('utf-8').strip() +"</a> (" + str(entries.count) + ")")
        	output.append("<a href=" + entries.url.encode('utf-8').strip() + ">" + entries.reponame.encode('utf-8').strip() +"</a>")                        


    #Empty array?
	if len(output) !=0 : 
 		outputString = "<br/><b>Similar Repositories</b>: "
 		outputString +=  ", ".join(output)
	
	app.logger.debug ("Sending ......", outputString)
	return(outputString)
