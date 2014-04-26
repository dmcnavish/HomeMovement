import upload_data
import upload_vids

def upload_all():
	upload_data.execute_upload()
	upload_vids.execute_upload()

if __name__ == '__main__':
	upload_all()