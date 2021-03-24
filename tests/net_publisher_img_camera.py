from zenoh_service.core.zenoh_net import ZenohNet
from zenoh_service.zenoh_net_publisher import ZenohNetPublisher
import sys
import time
from datetime import datetime
import numpy as np
import cv2
import simplejson as json
from enum import Enum
import logging

# Enable / disable cvout
_enable_cv_out = False

# Encoding parameter
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # The default value for IMWRITE_JPEG_QUALITY is 95

###

L = logging.getLogger(__name__)


###

def encrypt_str(str_val, byteorder="little"):
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val  # max 19 digit


# Define input data
# [1] Data Type: simple Integer / Float / Bool
# encoder_format = None
# itype = 1
# val = 123
###############################################################

# [2] Data Type: Numpy Array (image)
# encoder_format = None
# itype = 2
# root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# val = cv2.imread(root_path)
###############################################################

# [3] Data Type: Numpy Array with structured array format (image + other information)
# itype = 3
# encoder_format = [
# 	('id', 'U10'),
# 	('timestamp', 'f'),
# 	('data', [('flatten', 'i')], (1, 6220800)),
# 	('store_enabled', '?'),
# ]
# root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# img = cv2.imread(root_path)
# img_1d = img.reshape(1, -1)
# val = [('Drone 1', time.time(), img_1d, False)]
###############################################################

# # Scenario 1: Simple Pub/Sub with a single PC
# selector = "/demo/**"

# Scenario 2: Pub/Sub with two hosts
"""
	Simulated scenario:
	- `Host #01` will has IP `192.168.1.110`
	- `Host #01` run `subscriber`
	- `Host #02` run `publisher`
	- Asumming that both hosts are in the multicast network environment
"""
# selector = "/demo/**"
# peer = "tcp/172.18.8.188:7447"
# peer = "tcp/localhost:7446"
# peer = "tcp/140.113.193.134:7446"
peer = None

# configure zenoh service
path = "/eaglestitch/svc/zenoh-python-pub"
z_svc = ZenohNetPublisher(
	_path=path, _session_type="PUBLISHER", _peer=peer
)
z_svc.init_connection()

# register and collect publisher object
z_svc.register()
publisher = z_svc.get_publisher()

#########################
# Zenoh related variables
itype = 3
encoder_format = [
	('id', 'U10'),
	('timestamp', 'f'),
	('data', [('flatten', 'i')], (1, 6220800)),
	('store_enabled', '?'),
]

window_title = "output-raw"
# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/0312_2_CUT.mp4")
# cap = cv2.VideoCapture("/home/tim/devel/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4")
cap = cv2.VideoCapture("/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4")
if _enable_cv_out:
	cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
	# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
	cv2.resizeWindow(window_title, 800, 550)  # Enter your size
_frame_id = 0

_wt, _ht = 1080, 1920  # target width and height
_w, _h = None, None  # default detected width and height

# IMPORTANT
_is_compressed = True  # it enables/disables image compression when sending image frames

# Extra information (to be tagged into the frame)
int_drone_id = encrypt_str("Drone 01")  # contains 1 extra slot
t0_array = str(time.time()).split(".")  # contains 2 extra slots
extra_len = 5  # contains 1 extra slot; another one slot is from `tagged_data_len` variable

while cap.isOpened():
	_frame_id += 1
	# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
	try:
		ret, frame = cap.read()

		# do it ONCE
		# detect width and height
		if _w is None:
			_w, _h, _ = frame.shape

		t0_decoding = time.time()
		# resize the frame; Default VGA (640 x 480) for Laptop camera
		if _w != _wt:
			frame = cv2.resize(frame, (1920, 1080))

		# compress image (if enabled)
		if _is_compressed:
			# NEW encoding method
			# print(" ### compress image (if enabled)")
			encoder_format = None  # disable custom encoder
			itype = 4  # new type specially for compressed image
			t0_img_compression = time.time()
			_, compressed_img = cv2.imencode('.jpg', frame, encode_param)
			compressed_img_len, _ = compressed_img.shape
			t1_img_compression = (time.time() - t0_img_compression) * 1000
			print(('[%s] Latency Image Compression (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_img_compression)))
			tagged_data_len = compressed_img_len + extra_len  # `tagged_data_len` itself contains 1 extra slot
			# cv2.imwrite("hasil.jpg", decimg)

			# vertically tag this frame with an extra inforamtion
			t0_tag_extraction = time.time()
			tagged_info = [
				[int_drone_id],
				[int(t0_array[0])],
				[int(t0_array[1])],
				[extra_len],
				[tagged_data_len],
			]
			# print(" ----- OLD SHAPE compressed_img:", compressed_img.shape)
			val = np.vstack([compressed_img, tagged_info])
			t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
			print(('[%s] Latency Image Taging (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_tag_extraction)))
		else:
			# OLD enconding method
			val = [('Drone 1', time.time(), frame.tobytes())]
			t1_decoding = (time.time() - t0_decoding) * 1000
			print(('\n[%s] Latency tagging (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		# OLD enconding method
		# # img_1d = frame.reshape(1, -1)
		# # val = [('Drone 1', time.time(), img_1d, False)]
		# # val = [('Drone 1', time.time(), imgencode, False)]
		# val = [('Drone 1', time.time(), imgencode.tobytes())]
		# t1_decoding = (time.time() - t0_decoding) * 1000
		# print(('\n[%s] Latency tagging (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		# publish in every 10 frames
		if ret and _frame_id % 2 == 0:
			# publish data
			z_svc.publish(
				_val=val,
				_itype=itype,
				_encoder=encoder_format,
			)

		# time.sleep(1)

		if _enable_cv_out:
			cv2.imshow(window_title, frame)
		print()
	except Exception as e:
		print("No more frame to show: `{}`".format(e))
		break

	if _enable_cv_out:
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

if _enable_cv_out:
	# The following frees up resources and closes all windows
	cap.release()
	cv2.destroyAllWindows()
#########################

# n_epoch = 5  # total number of publication processes
# # for i in range(n_epoch):
# while True:
# 	# publish data
# 	z_svc.publish(
# 		_val=val,
# 		_itype=itype,
# 		_encoder=encoder_format,
# 	)
#
# 	time.sleep(0.33)

# closing Zenoh publisher & session
z_svc.close_connection(publisher)
