GitHub Analytics
===============

Analyze GitHub public timeline to provide valuable insights.

### Usage 
1. Sign up for Bigquery (https://developers.google.com/bigquery/sign-up)
2. Rename config-sample.py as config.py
   * Fill PROJECT_NUMBER
   * Fill SERVICE_ACCOUNT_EMAIL
   * Add key
6. Run Trainman.py
7. Run RunFlash.py
8. Visit localhost:5000 

````
$> python Trainman.py
#Generates output on screen
#Stores output in JSON format inside  app/data/toprepositories.json

$> python RunFlask.py
#Start Flask
````

