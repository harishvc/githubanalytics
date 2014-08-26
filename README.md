GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

Python & Node.js are used in this project. Node.js is used for fetching and parsing public activity from GitHub Archive. 
Python is used for processing and hosted using the Flask framework. 

### Usage 
* Get GitHub Archive public activity for the past hour
````
$> node FetchParseGitHubArchive.js  
#Generates app/data/PushEvent.json with PushEvent
```` 
* Start Flask
````
$> python RunFlash.py
# Host and port  displayed
````

* Visit localhost:5000 

* Sample output
![picture alt](https://github.com/harishvc/githubanalytics/blob/master/pics/sample-output.png "GitHub Analytics")

###TODO
1. Deploy app (ran into issues deploying on Heroku)
2. Integrate with GitHub API to provide more information about users and repositories
3. Inegrate with Neo4j to depelop recmmendations
