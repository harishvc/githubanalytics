import json
from pprint import pprint
json_data=open('./data/PushEvent.json')
data = json.load(json_data)
import operator


def find_term(term,type,max):
    d = dict()
    d2 = dict()
    for key, value in data.items():
        if value[term] in d:
            d[value[term]] += 1
        else:
            d[value[term]] = 1
         
    d2 = sorted(d.iteritems(), key=lambda (k,v): (v,k),reverse=type)[:max]
    return d2
  
def find_active_repositories(what,max):
    d = {}
    term=what
    for key, value in data.items():
        if value[term] in d:
            d[value[term]]['count'] +=1            
        else:
            tmp1 = {'count':1,'name':value['name'],'url':value['url'],'language':value['name'],'description':value['description']}
            d[value[term]] = tmp1

    return sorted(d.iteritems(), key=lambda (x, y): (y['count']),reverse=True)[:max]

def find_active_users(what,max):
    d = {}
    term=what
    for key, value in data.items():
        if value[term] in d:
            d[value[term]]['count'] +=1            
        else:
            tmp1 = {'count':1,'actorname':value['actorname'],'actorlogin':value['actorlogin']}
            d[value[term]] = tmp1
            
    return sorted(d.iteritems(), key=lambda (x, y): (y['count']),reverse=True)[:max]


#Total commits
print '#Commits', "{:,}".format(len(data))

#Find Top Languages
print "\nTop Languages ###"
languages = dict()
languages = find_term("language",True,5)
for key, value in languages:
        print "%s: %s" % (key, value)
 
        
#Find active repositories
print "\nActive Repositories ###"
repositories= dict()
repositories = find_active_repositories("url",6)
for key, value in repositories:
    print "%s %s" % (value['url'], value['count'])


#Find active users
print "\nActive users ###"
users= dict()
users = find_active_users("actorlogin",6)
for key, value in users:
    print "%s %s %s" % (value['actorname'],value['actorlogin'],value['count'])
    
    
#Close
json_data.close()
