[![Travis CI](https://travis-ci.org/harishvc/githubanalytics.svg)](https://travis-ci.org/harishvc/githubanalytics.svg)  
[![Sauce Test Status](https://saucelabs.com/buildstatus/harishvc)](https://saucelabs.com/buildstatus/harishvc)

GitHub Analytics
===============

Analyze GitHub public timeline &amp; provide insights.

Developed using Python &amp; Node.js using NoSQL databases [MongoDB](http://www.mongodb.org/) &amp; [Neo4j](http://neo4j.com/). Hosted on [Heroku](https://www.heroku.com/) 
and powered by [Compose](https://www.compose.io/).
* Fetch and parse public GitHub activity from [GitHub Archive](https://www.githubarchive.org/). Event type ```PushEvent``` are parsed using Node.js and inserted into MongoDB 
* Nodes and relations are built using Cypher query language and inserted into Neo4j for insights and recommendations 
* Application is developed in Python using Flask framework
* Interested? Visit [Ask GitHub](http://askgithub.com)

### Deployment Steps
Step1: Set environment variables
````
deployEnv=""           #production or development
PORT=5000              #non-standard port
#Heroku specific for Python & node.js
BUILDPACK_URL="https://github.com/ayyar/heroku-buildpack-python-nodejs"   

#Production specific environment variables
connectURL=""          #mongo connect URL
connectURLRead=""      #mongo connect URL for readonly account
database=""            #database name
mycollection=""        #collection name

#Development specific environment variables
connectURLdev=""       #mongo connect URL
databasedev=""         #database name
mycollectiondev=""     #collection name
myIP=""                #development server IP address

#Neo4j specific environment variable
neoURL=""              #neo4j connection string
```` 

Step 2: Get GitHub Archive public activity for the past hour
````
$> node FetchParseGitHubArchive.js //Add this script to Heroku scheduler 
```` 

Step 3: Start Flask
````
$> python RunFlash.py
# Procfile used for Heroku deployment
````

Step 4: Visit localhost:5000 

Step 5: Integration with Neo4j (optional)
````
$>cd bin                               #bin folder inside repository
$>python GenerateCypher.py             #build nodes and relations
$>cd /local/neo4j/bin                  #neo4j location
$>./neo4j-shell -file /path-to-cypher  #import cypher from neo4j shell
$>cd bin                               #bin folder inside repository
$>python MongoInsert.py                #insert recommendations inside mongo
````

### Hosted on [Heroku](https://www.heroku.com/) and powered by [Compose](https://www.compose.io/)
Interested? Visit [Ask GitHub](http://askgithub.com)


### Neo4j 2015 Data Challenge
Ask [GitHub GraphGist](http://gist.neo4j.org/?d9adad5c248385bea68c) won the [2015 Neo4j Data Challenge in the category Creative Graph Search and Insights](http://neo4j.com/blog/winners-neo4j-graphgist-winter-challenge-2015/)

### 2014 GitHub Data Challenge
branch "datachallenge" contains the code branch for GitHub <a href="https://github.com/blog/1864-third-annual-github-data-challenge">third annual data challenge</a>


###TODO
[Open issues on GitHub](https://github.com/harishvc/githubanalytics/issues)

[![Analytics](https://ga-beacon.appspot.com/UA-55381661-1/githubanalytics/readme)](https://github.com/igrigorik/ga-beacon)
