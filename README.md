GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

Developed using Python &amp; Node.js using NoSQL databases MongoDB &amp; Neo4j. Hosted on [Heroku](https://www.heroku.com/) and powered by [Compose](https://www.compose.io/)
* Node.js script fetch and parse public GitHub activity. Event type ```PushEvent``` are parsed from [GitHub Archive](https://www.githubarchive.org/) and stored in MongoDB 
* Nodes and relations are built in Cypher and inserted into Neo4j for insights and recommendations 
* Application is developed in Python using the Flask framework
* Interested? Visit [AskGitHub](http://aksgithub.com)

### Usage
1. Set environment variables
````
export deployEnv=""    #enter production or development
export PORT=5000       #pick a non-standard port
BUILDPACK_URL="https://github.com/ayyar/heroku-buildpack-python-nodejs"  #Heroku specific for Python & node.js 

#Production specific environment variables
connectURL=""          #enter mongo connect URL
connectURLRead=""      #enter mongo connect URL for readonly account
database=""            #enter database name
mycollection=""        #enter collection name

#Development specific environment variables
connectURLdev=""       #enter mongo connect URL
databasedev=""         #enter database name
mycollectiondev=""     #enter collection name
myIP=""                #enter development server IP address

#Neo4j specific environment variable
neoURL=""              #enter neo4j connection string
```` 
2. Get GitHub Archive public activity for the past hour
````
$> node FetchParseGitHubArchive.js //Add this script to Heroku scheduler 
```` 
3. Start Flask
````
$> python RunFlash.py
# Procfile used for Heroku deployment
````
4. Visit localhost:5000 

5. Integration with Neo4j (optional)
````
$>cd bin                               #bin folder inside repository
$>python GenerateCypher.py             #build nodes and relations
$>cd /local/neo4j/bin                  #neo4j location
$>./neo4j-shell -file /path-to-cypher  #import cypher from neo4j shell
$>cd bin                               #bin folder inside repository
$>python MongoInsert.py                #insert recommendations inside mongo
````

### Hosted on [Heroku](https://www.heroku.com/) and powered by [Compose](https://www.compose.io/)
Interested? Visit [AskGitHub](http://aksgithub.com)

### GitHub Data Challenge
branch "datachallenge" contains the code branch for GitHub <a href="https://github.com/blog/1864-third-annual-github-data-challenge">third annual data challenge</a>


###TODO
1. Enable cache
2. Integrate with GitHub API to provide real-time information about users and repositories

[![Analytics](https://ga-beacon.appspot.com/UA-55381661-1/githubanalytics/readme)](https://github.com/igrigorik/ga-beacon)
