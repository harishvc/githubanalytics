#Source: https://developers.google.com/bigquery/docs/authorization#service-accounts-server
# https://developers.google.com/bigquery/bigquery-api-quickstart#query
# start here -> https://developers.google.com/bigquery/docs/developers_guide
# https://developers.google.com/bigquery/querying-data
# copied from https://developers.google.com/bigquery/bigquery-api-quickstart#completecode
#Check for tab and spacing
# $>python -m tabnanny test.py 

import httplib2
import pprint
import sys
import time
import json
import logging
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient import errors
from pprint import pprint
from datetime import datetime, timedelta
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from config import config 

#Debug
# https://developers.google.com/api-client-library/python/guide/logging
#httplib2.debuglevel = 4
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

#Read from external configuration file
PROJECT_NUMBER = config['PROJECT_NUMBER']
SERVICE_ACCOUNT_EMAIL = config['SERVICE_ACCOUNT_EMAIL']

def main():
	
    f = file(config['KEY_FILE'], 'rb')    
    key = f.read()
    f.close()
    credentials = SignedJwtAssertionCredentials(
    		SERVICE_ACCOUNT_EMAIL,
    		key,
    		scope='https://www.googleapis.com/auth/bigquery.readonly')
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    bigquery_service = build('bigquery', 'v2', http=http)

    #https://code.google.com/p/python-sqlparse/
    #http://sqlformat.org/
    try:
        print "#Start: %s" % (datetime.today().strftime('%Y-%m-%d %H:%M:%S'))   
        
        #Time 24 hours ago
        lastHourDateTime = datetime.today() - timedelta(hours = 24)
        aa = lastHourDateTime.strftime('%Y-%m-%d %H:%M:%S')      
        #aa = "2014-08-15 00:00:00"   #DEVELOPMENT + CACHE
        
        query_request = bigquery_service.jobs()
        #https://developers.google.com/bigquery/docs/reference/v2/jobs/query
        myquery = 'SELECT repository_name, COUNT(repository_name) AS cnt, \
                                    repository_language, \
                                    repository_description, \
                                    repository_url \
                            FROM githubarchive:github.timeline \
                            WHERE TYPE="WatchEvent" \
                              AND PARSE_UTC_USEC(created_at) >= PARSE_UTC_USEC("'+ aa +'") \
                              AND repository_url IN \
                                (SELECT repository_url \
                                 FROM githubarchive:github.timeline \
                                 WHERE TYPE="CreateEvent" \
                                   AND PARSE_UTC_USEC(repository_created_at) >= PARSE_UTC_USEC("'+ aa +'") \
                                   AND repository_fork = "false" \
                                   AND payload_ref_type = "repository" \
                                 GROUP BY repository_url) \
                            GROUP BY repository_name, \
                                     repository_language, \
                                     repository_description, \
                                     repository_url HAVING cnt >= 5 \
                            ORDER BY cnt DESC LIMIT 5;'
        query_data = {
                   "kind": "bigquery#job",
                   'query': myquery,
                     "useQueryCache": "True"  # True or False                         
                     }
        
        #Trigger on-demand query
        #Quota & Policy info https://developers.google.com/bigquery/quota-policy                         
        query_response = query_request.query(projectId=PROJECT_NUMBER,body=query_data).execute()
        
        #Did the bigquery get processed?
        if ((query_response['jobComplete']) and (int(query_response['totalRows']) >1) and (int(query_response['totalBytesProcessed']) > 100 )):
            print "Success: jobComplete=%s \t totalRows=%s \t totalBytesProcessed=%s" % (query_response['jobComplete'],query_response['totalRows'], query_response['totalBytesProcessed'])
            #Store result for further analysis
            with open( 'app/data/toprepositories.json', 'w' ) as outfile:
                json.dump( query_response,outfile)
        else:
            print "Ignore ####"

        #Print results        
        print "Top Repositories in Github"
        #print query_response  #JSON output
        for row in query_response['rows']:
            result_row = []
            for field in row['f']:
                result_row.append(field['v'])
            print('\t'.join(map(str,result_row)))

        print "#End: %s" % (datetime.today().strftime('%Y-%m-%d %H:%M:%S'))   
            
    except HttpError as err:
    		print "Error:", pprint(err.content)
    
    except AccessTokenRefreshError:
    		print "Token Error: Credentials have been revoked or expired"
    
if __name__ == '__main__':
	main()
