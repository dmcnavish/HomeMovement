#!/usr/bin/env python

import time
import os
import datetime
from os import listdir
from os.path import isfile, join
import MySQLdb
import sys
import traceback

# def getCurrentTime():
# 	return datetime.datetime.fromtimestamp(time.time())

def formatTime(t):
	return str(datetime.datetime.fromtimestamp(t))

def insertRow(camera, filename, frame, file_type, time_stamp_date, time_stamp_time, event_time_stamp, x,y):
	db = None
	try:
		db = MySQLdb.connect("localhost", "motion_user", "m0t1on", "pi_motion")
		curs=db.cursor()
		sql = "INSERT INTO security (camera, filename, frame, file_type, utc_create_date, text_event, x,y) "
		sql += " values(" + camera + ",'"+filename+"',"+str(frame)+","+str(file_type)+",'"+str(time_stamp_date)+" " + str(time_stamp_time)+"',"+str(event_time_stamp)+","+x+","+y+")"
		print sql
		curs.execute(sql)
		db.commit()
		print 'row inserted'
	except:
		tb = traceback.format_exc()
		print 'failed to insert:\n {0}'.format(tb)
	finally:
		db.close()
		# print 'connection closed'

def cleanup_files():
	print 'args: ' + str(sys.argv)
	insertRow(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])

	#clean up any files that are older than 10 minutes
	cleanup_dir = '/home/pi/motion_tmp/'
	allfiles = listdir(cleanup_dir)

	total_deleted = 0
	for f in allfiles:
		full_path = cleanup_dir + f
		if '.avi' not in full_path and '.jpg' not in full_path:
			continue
		if '.avi' in full_path:
			continue
		modDate = os.path.getmtime(full_path)
		if modDate < (time.time() - (60*10)):
			print 'deleting: ' + full_path + ' last edited: ' + formatTime(modDate) 
			os.remove(full_path)
			total_deleted += 1
		#else:
			#print 'file is not old enough to delete: ' + formatTime(modDate)

	print 'total files deleted: ' + str(total_deleted)

if __name__ == '__main__':
	cleanup_files()
