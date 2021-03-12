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

###

L = logging.getLogger(__name__)


###


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
peer = "tcp/localhost:7446"

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
cap = cv2.VideoCapture("/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/0312_2_CUT.mp4")
cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
cv2.resizeWindow(window_title, 800, 550)  # Enter your size
_frame_id = 0
while cap.isOpened():
	_frame_id += 1
	# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
	try:
		ret, frame = cap.read()

		# resize the frame; Default VGA (640 x 480)
		frame = cv2.resize(frame, (1920, 1080))

		img_1d = frame.reshape(1, -1)
		val = [('Drone 1', time.time(), img_1d, False)]

		# publish in every 10 frames
		if ret and _frame_id % 10 == 0:
			# publish data
			z_svc.publish(
				_val=val,
				_itype=itype,
				_encoder=encoder_format,
			)

		# time.sleep(1)

		cv2.imshow(window_title, frame)
	except Exception as e:
		print("No more frame to show: `{}`".format(e))
		break

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
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
