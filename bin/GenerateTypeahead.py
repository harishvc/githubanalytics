from pymongo import MongoClient
import os.path, time
import json
from json import dumps

LimitActiveRepositories=5

def ActiveRepositories ():
    pipeline= [
           { '$match': {}}, 
           { '$group': {'_id': {'url': '$url',  'name': "$name", 'language': "$language", 'description': "$description"}}},
           { '$project': { '_id': 0, 'url': '$_id.url', 'name': "$_id.name", 'language': "$_id.language", 'description': "$_id.description"} },
           #{ '$sort' : { 'count': -1 }},
           #{ '$limit': LimitActiveRepositories}
           ]
    mycursor = db.aggregate(pipeline)
    #print "#############" , mycursor['result']
    return mycursor


def GActiveRepositories():
    output = []
    mycursor = ActiveRepositories()
    #print "#############" , mycursor['result']
    for record in mycursor["result"]:
        #print record['name'] , record['language'], record['description']
        if (str(record['language']) != 'None'):
            output.append({"label": "repository " +  str(record['name']),  "url": str(record['url']) , "tokens": [str(record['name']),str(record['language'])]})
        else:
            output.append({"label": "repository " + str(record['name']), "url": str(record['url']), "tokens": [str(record['name'])]})    
    
    #Convert single quote to double quote
    jsonString = json.dumps(output)
    #print jsonString       
    text_file = open("../static/typeahead/repos.json", "w")
    text_file.write(jsonString)
    text_file.close()
    
    
        
#Configure DB using environment variables
MONGO_URL = os.environ['connectURLRead']
connection = MongoClient(MONGO_URL)
db = connection.githublive.pushevent

#Generate Repositories JSON
GActiveRepositories() 


#Close db
connection.close()