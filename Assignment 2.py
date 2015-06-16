__author__ = 'Steve_Jobs'

'''Name:Pavan Ghanta
   Course:CSE 6331
   Lab:Assignment 2'''

import os
#Referenced from Assignment 1
import argparse
import httplib2
import urllib
import os
import sys
import json
import time
import datetime
import io
import hashlib
import logging
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
import apiclient.http
data_dir=os.path.dirname(__file__)
srcfileurl='http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv'
srcfilename='all_month.csv'
#Referenced from Assignment 1
_BUCKET_NAME = 'paghanta'
_API_VERSION = 'v1'
__PROJECT_ID='p9v9n261-971'
__INSTANCE__NAME='earthquakedata'
__DATABASE__NAME='30DAYSDATA'
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
# client_secret.json is the JSON file that contains the client ID and Secret.
#You can download the json file from your google cloud console.
CLIENT_SECRETS = os.path.join(data_dir, 'client_secret.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes.
# These scopes are used to restrict the user to only specified permissions (in this case only to devstorage)
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/devstorage.full_control',
      'https://www.googleapis.com/auth/devstorage.read_only',
      'https://www.googleapis.com/auth/devstorage.read_write',
      'https://www.googleapis.com/auth/sqlservice.admin',
      'https://www.googleapis.com/auth/cloud-platform'
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

def copytocloud(service):
    srcfile=open(os.path.join(data_dir,srcfilename))
    srcfiledata=srcfile.read()
    fileio = io.BytesIO()
    fileio.write(srcfiledata)
    uploadfile = apiclient.http.MediaIoBaseUpload(fileio, '[*/*]')
    uploadrequest = service.objects().insert(bucket=_BUCKET_NAME,name=srcfilename,media_body=uploadfile)
    try:
        uploadresponse = uploadrequest.execute()
        print 'File copy completed'
    except:
        print('Failed to upload')



def main(argv):
    #Referenced from assignment1
    flags = parser.parse_args(argv[1:])
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Cloud Storage API.
    service = discovery.build('storage', _API_VERSION, http=http)

    # copytocloud(service)
    # dburl='https://www.googleapis.com/sql/v1beta4/projects/'+__PROJECT_ID+'/instances/'+__INSTANCE__NAME+'/databases/'
    # reqbody={"instance":__INSTANCE__NAME,"name":__DATABASE__NAME,"project":__PROJECT_ID,"kind": "sql#database"}
    # reqbody=urllib.urlencode(reqbody)
    # response= http.request(dburl,'POST',reqbody)
    # print(response)
    # print("pavan")
    dburl='https://www.googleapis.com/sql/v1beta4/projects/'+__PROJECT_ID+'/instances/'+__INSTANCE__NAME+'/import'
    reqbody={"importContext": {
                "kind": "sql#importContext",
                "fileType": "CSV",
                "uri": "gs://"+_BUCKET_NAME+"/"+srcfilename,
                "database": "test",
                "csvImportOptions": {
                  "table": "30days",
                  "columns": [
                    "time"
                             ]
                    }
                }
            }
    response= http.request(dburl,'POST',body=urllib.urlencode(reqbody))
    print(response)
    print("pavan")

if __name__ == '__main__':
  main(sys.argv)