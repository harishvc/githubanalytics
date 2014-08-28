#!flask/bin/python
#old
#from app import app
#app.run(debug = True)
#app.run(host="glacial-lake-7558.herokuapp.com",port="5000")

#new
#http://stackoverflow.com/questions/13714205/deploying-flask-app-to-heroku
import os  
from app import app  
port = int(os.environ.get('PORT', 5000)) 
app.run(debug = True)
print "starting flask server hostname:% port:%" % (host, port)
app.run(host='0.0.0.0', port=port)
