# Copyright (c) 2017, 2020 ADLINK Technology Inc.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ADLINK zenoh team, <zenoh@adlink-labs.tech>

# Examples
# HOST1 $ zn_sub -l tcp/<IP HOST1>:7447
# HOST2 $ zn_pub -e tcp/<IP HOST1>:7447


import sys
import time
import argparse
import itertools
import zenoh
from zenoh.net import config
import cv2
from datetime import datetime
import numpy as np

# Encoding parameter
# The default value for IMWRITE_JPEG_QUALITY is 95
# Source: https://stackoverflow.com/questions/40768621/python-opencv-jpeg-compression-in-memory
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
	prog='zn_pub',
	description='zenoh-net pub example')
parser.add_argument('--mode', '-m', dest='mode',
					choices=['peer', 'client'],
					type=str,
					help='The zenoh session mode.')
parser.add_argument('--peer', '-e', dest='peer',
					metavar='LOCATOR',
					action='append',
					type=str,
					help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--listener', '-l', dest='listener',
					metavar='LOCATOR',
					action='append',
					type=str,
					help='Locators to listen on.')
parser.add_argument('--path', '-p', dest='path',
					default='/demo/example/zenoh-python-pub',
					type=str,
					help='The name of the resource to publish.')
parser.add_argument('--value', '-v', dest='value',
					default='Pub from Python!',
					type=str,
					help='The value of the resource to publish.')
parser.add_argument('--config', '-c', dest='config',
					metavar='FILE',
					type=str,
					help='A configuration file.')

args = parser.parse_args()
conf = zenoh.config_from_file(args.config) if args.config is not None else {}
if args.mode is not None:
	conf["mode"] = args.mode
if args.peer is not None:
	conf["peer"] = ",".join(args.peer)
if args.listener is not None:
	conf["listener"] = ",".join(args.listener)
path = args.path
value = args.value

# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---

# initiate logging
zenoh.init_logger()

print("Openning session...")
session = zenoh.net.open(conf)

print("Declaring Resource " + path)
rid = session.declare_resource(path)
print(" => RId {}".format(rid))

print("Declaring Publisher on {}".format(rid))
publisher = session.declare_publisher(rid)

root_path = "./../data/out1.png"
frame = cv2.imread(root_path)
print("SHAPE: ", frame.shape)

t0_decoding = time.time()
result, imgencode = cv2.imencode('.jpg', frame, encode_param)
# result, imgencode = cv2.imencode('.png', frame, encode_param)
data = np.array(imgencode)
print(" SHAPE data:", data.shape)
t1_decoding = (time.time() - t0_decoding) * 1000
print(('\n[%s] Latency imgencode (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

t0_decoding = time.time()
# stringData = data.tostring()
# print(" ---- TYPE:", type(stringData))
encoded_data = data.tobytes()
# bytes_data = bytes(stringData, encoding='utf8')
# buf = "[{:4d}] {}".format(1, encoded_data)
# buf = "[{:4d}] {}".format(1, stringData)
# bytes_data = bytes(buf, encoding='utf8')
# print(buf)
t1_decoding = (time.time() - t0_decoding) * 1000
print(('\n[%s] Latency tostring (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
print(" ---- STRING len stringData: ", len(encoded_data))

for idx in itertools.count():
	# time.sleep(0.33)
	# buf = "[{:4d}] {}".format(idx, value)
	# buf = "[{:4d}] {}".format(idx, stringData)
	# print(" --- sending Bytes image..")
	# print("[{}] Writing Data ('{}': '{}')...".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), rid, buf))
	# session.write(rid, bytes(buf, encoding='utf8'))
	session.write(rid, encoded_data)
	# session.write(rid, bytes_data)
	# session.write(rid, stringData)

publisher.undeclare()
session.close()
