#Source: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates

from flask import render_template
from app import app
import json
from datetime import datetime, timedelta
import os.path, time

# configuration
JSON_DATA = 'app/data/toprepositories.json'
DEBUG = True
f = open(JSON_DATA, 'r')
data = json.load(f)
f.close()

mydata = []
for row in data['rows']:
            #print ("\n")
            result_row = []
            for field in row['f']:
                    #print (field['v'])
                    result_row.append(field['v'])
            #print "new entry!!!"
            #print result_row
            #print('\t'.join(map(str,result_row)))
            mydata.append({'name': result_row[0], 'count' : result_row[1], 
                         'lang': result_row[2], 'desc' : result_row[3],'url': result_row[4]})

#now = datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " PSD"
now = time.ctime(os.path.getmtime(JSON_DATA))

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'GitHub Analytics',
        time  = now,
        data = mydata )
