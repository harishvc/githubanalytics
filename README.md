GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

### Usage 
1. Sign up for Bigquery (https://developers.google.com/bigquery/sign-up)
2. Rename config-sample.py as config.py
4. Fill PROJECT_NUMBER
5. Fill SERVICE_ACCOUNT_EMAIL
6. Add key
5. Run script
````
$> python Trainman.py
#Generated output on screen
#Stores output in JSON format in app/data/toprepositories.json
```
6. Start Flask
```
$> python RunFlask.py
````
7. Visit localhost:5000 to see top repositories
