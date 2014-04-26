import upload_vids
import unittest

class UploadVidsTest(unittest.TestCase):
		def test_join(self):
			files='/home/pi/motion_tmp/1287-20140223224143.avi|/home/pi/motion_tmp/1286-20140223223603.avi'
			root_dir='/home/pi/motion_tmp'
			output_file = upload_vids.join_video_files(files, root_dir)
			print 'output_file: ' + output_file

if __name__ == '__main__':
	unittest.main()