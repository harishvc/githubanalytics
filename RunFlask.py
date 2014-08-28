import os  
from app import app  
port = int(os.environ.get('PORT', 5000)) 
app.run(debug = True)
print "starting flask server hostname:% port:%" % (host, port)
app.run(host='0.0.0.0', port=port)
