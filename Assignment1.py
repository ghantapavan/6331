'''Copyright (c) 2015 HG,DL,UTA
   Python program runs on local host, uploads, downloads, encrypts local files to google.
   Please use python 2.7.X, pycrypto 2.6.1 and Google Cloud python module '''

#import statements.
import argparse
import httplib2
import os
import sys
import json
import time
import datetime
import io
import hashlib
#Google apliclient (Google App Engine specific) libraries.
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
import apiclient.http
#pycry#pto libraries.
from Crypto import Random
from Crypto.Cipher import AES
data_dir=os.path.dirname(__file__)

# Encryption using AES
#http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto


#Initial password to create a key


#this implementation of AES works on blocks of "text", put "0"s at the end if too small.
def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

#Function to encrypt the message
def encrypt(message, key, key_size=256):
    message = pad(message)
    #iv is the initialization vector
    iv = Random.new().read(AES.block_size)
    #encrypt entire message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

#Function to decrypt the message
def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

#Function to encrypt a given file
def encrypt_file(file_name, key):
    filepath=os.path.join(data_dir,file_name)
    ipfile=open(filepath,'rb')
    filedata=ipfile.read()
    encrypteddata=encrypt(filedata,key)
    encfilename="enc_"+file_name
    encfilepath=os.path.join(data_dir,encfilename)
    encfile=open(encfilepath,'wb')
    encfile.write(encrypteddata)
    return encfilename

	#Open file to read content in the file, encrypt the file data and
	#create a new file and then write the encrypted data to it, return the encrypted file name.



#Function to decrypt a given file.
def decrypt_file(file_name, key):
	#open file read the data of the file, decrypt the file data and 
	#create a new file and then write the decrypted data to the file.
    ipfile1=open(os.path.join(data_dir,file_name),'rb')
    encfiledata=ipfile1.read()
    decrypeddata=decrypt(encfiledata,key)
    decfilename=file_name[4:]
    decfile=open(os.path.join(data_dir,decfilename),'wb')
    decfile.write(decrypeddata)
    return decfilename






_BUCKET_NAME = 'paghanta' #name of your google bucket.
_API_VERSION = 'v1'

# Parser for command-line arguments.
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
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

#Downloads the specified object from the given bucket and deletes it from the bucket.
def get(service):
  #User can be prompted to input file name(using raw_input) that needs to be be downloaded, 
  #as an example file name is hardcoded for this function.
  downloadfilename=raw_input("Enter the filename to download:")
  try:
# Get Metadata
	req = service.objects().get(
        	bucket=_BUCKET_NAME,
        	object=downloadfilename,
        	fields='bucket,name,metadata(my-key)',    
        
                )                   
	resp = req.execute()
	print json.dumps(resp, indent=2)

# Get Payload Data
	req = service.objects().get_media(
        	bucket=_BUCKET_NAME	,
        	object=downloadfilename,
		)
# The BytesIO object may be replaced with any io.Base instance.
	fh = io.BytesIO()
	downloader = apiclient.http.MediaIoBaseDownload(fh, req, chunksize=1024*1024) #show progress at download
	done = False
	while not done:
	    status, done = downloader.next_chunk()
	    if status:
	        print 'Download %d%%.' % int(status.progress() * 100)
	    print 'Download Complete!'
	password=raw_input('Enter password to decrypt the file:')
	key = hashlib.sha256(password).digest()
	dec = decrypt(fh.getvalue(),key)
	with open(downloadfilename[4:], 'wb') as fo:
             fo.write(dec)
    	print 'File decryption completed'


  except client.AccessTokenRefreshError:
    print ("Error in the credentials")

    #Puts a object into file after encryption and deletes the object from the local PC.
def put(service):  
    print('Sample')
    filename=raw_input('Enter filename:')
    password =raw_input('Enter password to encrypt the file:')
    key = hashlib.sha256(password).digest()
    encrypted_file=encrypt_file(filename,key)
    encfile=open(os.path.join(data_dir,encrypted_file))
    encfiledata=encfile.read()
    fileio = io.BytesIO()
    fileio.write(encfiledata)
    media = apiclient.http.MediaIoBaseUpload(fileio, '[*/*]')
    req = service.objects().insert(
        bucket=_BUCKET_NAME,
        name=encrypted_file,
        media_body=media)
    success=False
    try:
        resp = req.execute()
        os.remove(os.path.join(data_dir,encrypted_file))
        os.remove(os.path.join(data_dir,filename))
        print 'File ecryption completed and uploaded to Google Cloud'
    except:
        print('Failed to upload')


	# '''User inputs the file name that needs to be uploaded.
	#    Encrypt the given file using AES encryption
	#    and then upload the file to your bucket on the google cloud storage.
	#    Remove the file from your local machine after the upload. '''


#Lists all the objects from the given bucket name
def listobj(service):
    listrequest = service.objects().list(bucket=_BUCKET_NAME)
    listresponse = listrequest.execute()
    print('List of files:')
    items=listresponse["items"]
    for eachitem in items:
        print(eachitem["name"])

#This deletes the object from the bucket
def deleteobj(service):
    deleteobject=raw_input("Enter the name of the object to delete:")
    deleterequest = service.objects().delete(bucket=_BUCKET_NAME,object=deleteobject)
    try:
        deleterequest.execute()
        print(deleteobject+' deleted successfully')
    except:
        print('Delete failed')

	
def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  
  #sample.dat file stores the short lived access tokens, which your application requests user data, attaching the access token to the request.
  #so that user need not validate through the browser everytime. This is optional. If the credentials don't exist 
  #or are invalid run through the native client flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file (sample.dat in this case). 
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

  #This is kind of switch equivalent in C or Java.
  #Store the option and name of the function as the key value pair in the dictionary.
  options = {1: put, 2: get, 3:listobj, 4:deleteobj}
  option =input('1: put, 2: get, 3:listobj, 4:deleteobj :')

   #Take the input from the user to perform the required operation.
  #for example if user gives the option 1, then it executes the below line as put(service) which calls the put function defined above.
  options[option](service)


if __name__ == '__main__':
  main(sys.argv)
# [END all]
