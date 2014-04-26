import pymongo
from pymongo import MongoClient
import datetime
import MySQLdb
import traceback


def mongo_insert(all_recs):
	try:
		client = MongoClient('mongodb://app_user:raspberry@ds029277.mongolab.com:29277/pi_security')
		db = client.pi_security
		records = db.records

		results = records.insert(all_recs)
		print 'total inserted: {0}'.format(len(results))
	except:
		tb = traceback.format_exc()
		print 'error inserting records into mongoDB: \n {0}'.format(tb)

# Expects a MySQLdb result row
def record_to_json(record):
	json = {"utcCreateDate": record[0],
			"x": record[1],
			"y": record[2]}
	# print 'json: ' + str(json)
	return json


def get_records():
	db = None
	try:
		db = MySQLdb.connect('localhost', 'motion_user', 'm0t1on', 'pi_motion')
		db.query('SELECT utc_create_date, x, y  FROM security WHERE utc_create_date between UTC_TIMESTAMP - INTERVAL 10 MINUTE and UTC_TIMESTAMP')
		records = db.store_result()
		total_results = db.affected_rows()
		print 'total: ' + str(total_results)
		all_recs = []
		for x in xrange(0, total_results):
			r = records.fetch_row()[0]
			# print 'r: ' + str(r)
			all_recs.append( record_to_json(r))

		return all_recs
	except:
		tb = traceback.format_exc()
		print 'error selecting records: \n {0}'.format(tb)
	finally:
		db.close()

def execute_upload():
	all_recs = get_records()
	print 'all_recs: {0}'.format(all_recs)
	mongo_insert(all_recs)

if __name__ == '__main__':
	execute_upload()