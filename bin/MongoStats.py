import os.path, time, sys
from pymongo import MongoClient
sys.path.append('../')
import MyMoment
import humanize


MONGO_URL = os.environ['connectURLRead']
connection = MongoClient(MONGO_URL)
db = connection.githublive

#client = MongoClient()
#db = client.test

# print collection statistics
stats = db.command("collstats", "pushevent")
#print stats
print "### " , MyMoment.MT()," MongoDB Stats ###"
print "Documents:",humanize.intcomma(stats['count'])
print "Size:",humanize.naturalsize(stats['size'])
print "Pre-allocated space:",humanize.naturalsize(stats['storageSize'])

 
# print database statistics
#print db.command("dbstats")
