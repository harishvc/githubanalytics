GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

Python & Node.js are used in this project. Node.js is used for fetching and parsing public activity from GitHub Archive. 
Python is used for processing and hosted using the Flask framework. 

### Usage 
1. Get GitHub Archive public activity for the past hour
````
$> node FetchParseGitHubArchive.js  
#Generates app/data/PushEvent.json with PushEvent
```` 
2. Start Flask
````
$> python RunFlash.py
# Host and port  displayed
````

3. Visit localhost:5000 

4. Sample output
[Github Analytics](http://github.com/harishvc/githubanalytics/pics/sample-output.png "GitHub Analytics")

###TODO
1. Deploy app (ran into issues deploying on Heroku)
2. Integrate with GitHub API to provide more information about users and repositories
3. Inegrate with Neo4j to depelop recmmendations
