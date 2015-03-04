import os.path, time, sys
from py2neo import neo4j,Graph,Node,Relationship

graph = Graph(os.environ['neoURLProduction'])

def numformat(value):
    return "{:,}".format(value)

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
    print output

#Determine edges and breakdown    
def Edges():
    for record in graph.cypher.execute("match (a)-[r]->(b) return count(r) as count"):
        total = numformat(record.count)
    for record in graph.cypher.execute("match (a:Repository)-[r]->(b:People) return count(r) as count"):
        RA = numformat(record.count)
    for record in graph.cypher.execute("match (a:Repository)-[r]->(b:Organization) return count(r) as count"):
        RO = numformat(record.count)
    output = "Relations:" + str(total) + " (" + "Repositories->People:" + str(RA) + ", Repositories->Organization:" + str(RO) + ")"        
    print output
    
	 		
Nodes()
Edges()
