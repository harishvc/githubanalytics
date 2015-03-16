import os
import sys
from StringIO import StringIO
import requests
sys.path.append('../')
import MyMoment

#Get rate limit for application

client_id = os.environ['github_client_id']
client_secret = os.environ['github_client_secret']
url ="https://api.github.com/rate_limit?client_id=" + client_id + "&client_secret=" + client_secret

response = requests.get(url)
print "Limit: " +  response.headers["X-RateLimit-Limit"] + " Remaining: " + response.headers["X-RateLimit-Remaining"] + " Reset: " + MyMoment.HTM(int(response.headers["X-RateLimit-Reset"]),"from now")
