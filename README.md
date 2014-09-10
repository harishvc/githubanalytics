GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

Python, MongoDB & Node.js are used in this project. Node.js is used for fetching and parsing public activity from GitHub Archive. 
Python is used for processing and hosted using the Flask framework. Data is stored in MongoDB and this project is hosted on Heroku.

### Usage
* Set environment variables
````
connectURL=""   //enter mongo connect URL
database=""     //enter database name
mycollection=""  //enter collection name
BUILDPACK_URL=https://github.com/ayyar/heroku-buildpack-python-nodejs  //Heroku specific for Python & node.js 
```` 
* Get GitHub Archive public activity for the past hour
````
$> node FetchParseGitHubArchive.js //Add this script to Heroku scheduler 
```` 
* Start Flask
````
$> python RunFlash.py
# Procfile used for Heroku deployment
````
* Visit localhost:5000 

### Deployed on Heroku
Visit <a href="http://rocky-hamlet-2442.herokuapp.com/">Github Analytics</a> to see this project in action!

### GitHub Data Challenge
branch "datachallenge" contains the code branch for GitHub <a href="https://github.com/blog/1864-third-annual-github-data-challenge">third annual data challenge</a>


###TODO
1. Enable cache
2. Integrate with GitHub API to provide more information about users and repositories
3. Inegrate with Neo4j to develop recommendations
