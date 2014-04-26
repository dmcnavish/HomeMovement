import httplib2
import pprint
import os.path
from datetime import date
import subprocess
import time

from os import listdir
from os.path import isfile
from oauth2client.client import Credentials
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

#check for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

def store_credentials(credentials):
	#TODO: replace with db call
	o = open('db.txt', 'wb')
	o.write(credentials.to_json())
	o.close()

#############################################################
# The properties specified in app.props are specific to this
# app and our Google account.
# client id and client secret arespecific to this app
# Redirect URL found in developer console under credentials
#############################################################
def get_props():
	props_file='/home/pi/scripts/drive_security/app.props'
	all_props = dict(line.strip().split('=') for line in open(props_file))
	# print 'all_props: ' + str(all_props)
	return all_props

def get_credentials():
	credentials = retrieve_credentials()
	if credentials is None:
		#run through the OAuth flow and retrieve credentials
		all_props = get_props()
		flow = OAuth2WebServerFlow(all_props['drive.client.id'], all_props['drive.client.secret'], OAUTH_SCOPE, all_props['drive.redirect.url'])
		# flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URL)
		authorize_url = flow.step1_get_authorize_url()
		print 'Go to the following link in your browser: ' + authorize_url
		#code = raw_input('Enter verification code: ').strip()
		code = 'nocode' #using for system run script
		credentials = flow.step2_exchange(code)
		if credentials.refresh_token is not None:
			store_credentials(credentials)
	return credentials

def retrieve_credentials():
	#TODO: replace with db call
	db_file='/home/pi/scripts/drive_security/db.txt'
	if os.path.isfile(db_file) == False:
		return None
	f = open(db_file)
	credentials = ''
	for line in f.read():
		credentials += line
	f.close()
	# print 'cred: ' + credentials
	if credentials.strip() == '':
		return None
	return Credentials.new_from_json(credentials)

def get_drive_service():
	credentials = get_credentials()
	#create an httplib2.http object and authorize it with our credentials
	http = httplib2.Http()
	http = credentials.authorize(http)

	drive_service = build('drive', 'v2', http=http)

	return drive_service

def insert_file(drive_parent_id, full_local_path, file_name, mime_type, desc=''):
	try:
		drive_service = get_drive_service()
		media_body = None
		if mime_type != 'application/vnd.google-apps.folder':
			media_body = MediaFileUpload(full_local_path, mimetype=mime_type, resumable=True)
		body = {
			'title': file_name,
			'description': desc,
			'mimeType': mime_type,
			'parents' : [{'id' : drive_parent_id}] #should put it in the root dir if not found
		}

		file = drive_service.files().insert(body=body, media_body=media_body, convert=True).execute()
		print 'File inserted. Drive Response:'
		#pprint.pprint(file)
		return file['id']
	except ValueError as e:
		print 'Error uploading file: ' + file_name + ' : ' + e

def create_folder(parent_id, folder_name):
	id = insert_file(parent_id, None, folder_name, 'application/vnd.google-apps.folder')
	print 'new folder (%s) created with id: %s' % (folder_name, str(id))

# def upload_file(drive_parent_id, file_name):
# 	try:
# 		drive_service = get_drive_service()

# 		#insert file
# 		mimeType = 'video/x-msvideo'  #text/plain
# 		media_body = MediaFileUpload(file_name, mimetype=mimeType, resumable=True)
# 		body = {
# 			'title': FILENAME,
# 			'description': 'A test document',
# 			'mimeType': mimeType,
# 			'parents' : [{'id' : drive_parent_id}]
# 		}

# 		file = drive_service.files().insert(body=body, media_body=media_body, convert=True).execute()
# 		print 'Drive Response:'
# 		pprint.pprint(file)
# 	except ValueError as e:
# 		print 'Error uploading file: ' + file_name + ' : ' + e

def upload_files(drive_root_id, root_dir='/home/pi/motion_tmp'):
	drive_parent_folder = get_parent_folder(drive_root_id)
	all_files=''
	files_to_delete = []
	for file_name in listdir(root_dir):
		full_path = root_dir + '/' + file_name
		if isfile(full_path) and '.avi' in full_path:
			print 'file to upload: ' + full_path
			all_files+=full_path + '|'
			files_to_delete.append(full_path)
			# upload_file(drive_parent_folder, full_path)
	# insert_file(drive_parent_folder, full_path, file_name, 'video/x-msvideo')
	if all_files != '':
		joined_file_name = join_video_files(all_files, root_dir)
		joined_file = root_dir + '/' + joined_file_name
		insert_file(drive_parent_folder, joined_file, joined_file_name, 'video/x-msvideo')
		os.remove(joined_file) #need to remove all
		for f in files_to_delete:
			os.remove(f)

def get_todays_folder():
	today = date.today().strftime("%m-%d-%Y")
	print 'today: ' + today
	return today

def join_video_files(all_files, output_dir):
	output_file_name = str(time.time()) + '.avi'
	output_file= output_dir + '/' + output_file_name
	avconv_command = ['avconv', '-i', 'concat:' + all_files, '-c', 'copy', output_file]
	subprocess.call(avconv_command)
	return output_file_name

# def create_folder(parent_id, folder_name):
# 	try:
# 		drive_service = get_drive_service()

# 		body = {
# 			'title': folder_name,
# 			'mimeType': 'application/vnd.google-apps.folder',
# 			'parents' : [{'id' : parent_id}]
# 		}

# 		file = drive_service.files().insert(body=body, convert=True).execute()
# 		print 'Drive Response:'
# 		pprint.pprint(file)
# 		return file['id']
# 	except ValueError as e:
# 		print 'Error uploading file: ' + file_name + ' : ' + e
# 		return None

def get_parent_folder(root_id):
	drive_service = get_drive_service()
	page_token = None
	todays_folder = get_todays_folder()
	while True:
		param = {}
		#check to see if there is already a folder for today
		param['q'] = "mimeType = 'application/vnd.google-apps.folder' and '%s' in parents and title contains '%s'" % (root_id, todays_folder)
		print 'param q: ' + param['q'] 
		if page_token:
			param['pageToken'] = page_token
		files = drive_service.files().list(**param).execute()

		for f in files['items']:
			print 'name: ' + f.get('title') + ' mimeType: ' + f.get('mimeType') + ' Id: ' + f.get('id')
			return f.get('id')
		# pprint.pprint(files['items'].get('mimeType'))
		page_token = files.get('nextPageToken')
		if not page_token:
			break;
	print 'parent directory not found! We will create it.'
	return create_folder(root_id, todays_folder)


def get_root_folder():
	drive_service = get_drive_service()
	page_token = None
	while True:
		param = {}
		param['q'] = "mimeType = 'application/vnd.google-apps.folder' and title = 'security'" #TODO: add additional checks to make sure there isn't more than one security folder
		if page_token:
			param['pageToken'] = page_token
		files = drive_service.files().list(**param).execute()

		for f in files['items']:
			print 'get_root_folder: name: ' + f.get('title') + ' mimeType: ' + f.get('mimeType') + ' Id: ' + f.get('id')
			return f.get('id')
		# pprint.pprint(files['items'].get('mimeType'))
		page_token = files.get('nextPageToken')
		if not page_token:
			break;
	print 'parent directory not found!'

def execute_upload():
	drive_root_id = get_root_folder()
	upload_files(drive_root_id)


if __name__ == "__main__":
	execute_upload()
	# drive_root_id = get_root_folder()
	# upload_files(drive_root_id)
	#get_todays_folder()
