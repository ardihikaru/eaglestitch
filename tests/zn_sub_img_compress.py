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
from datetime import datetime
import argparse
import zenoh
from zenoh.net import config, SubInfo, Reliability, SubMode
import time
import cv2
import numpy as np

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
	prog='zn_sub',
	description='zenoh-net sub example')
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
parser.add_argument('--selector', '-s', dest='selector',
					default='/demo/example/**',
					type=str,
					help='The selection of resources to subscribe.')
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
selector = args.selector

# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---


def decrypt_str(int_val, byteorder="little"):
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


def extract_drone_id(data, img_len):
	drone_idx = img_len + 1
	return decrypt_str(int(data[drone_idx][0]))


def extract_t0(data, img_len):
	to_p1_idx = img_len + 2
	to_p2_idx = img_len + 3

	t0 = "{}.{}".format(
		data[to_p1_idx][0],
		data[to_p2_idx][0],
	)
	return float(t0)


# def listener(sample):
def listener(consumed_data):
	"""
	Expected data model:
	[
		[img_data],  # e.g. 1000
		[drone_id],  # extra tag 01
		[t0_part_1],  # extra tag 02
		[t0_part_2],  # extra tag 03
		[total_number_of_tag],
		[tagged_data_len],  # total array size: `img_data` + `total_number_of_tag` + 1
	]
	"""
	print(" #### LISTENER ..")

	t0_decode = time.time()
	decoded_data = np.frombuffer(consumed_data.payload, dtype=np.int64)
	decoded_data_len = list(decoded_data.shape)[0]
	decoded_data = decoded_data.reshape(decoded_data_len, 1)
	array_len = decoded_data[-1][0]
	extra_tag_len = decoded_data[-2][0]
	encoded_img_len = array_len - extra_tag_len
	# print(" ----- decoded_data_len:", decoded_data_len)
	# print(" ----- array_len:", array_len)
	# print(" ----- extra_tag_len:", extra_tag_len)
	# print(" ----- encoded_img_len:", encoded_img_len)
	# print(" ----- SHAPE decoded_data:", decoded_data.shape)
	# decoded_data = np.frombuffer(encoded_data, dtype=np.uint64)
	# print(type(decoded_data), decoded_data.shape)
	# print(type(decoded_data))
	# print(" TAGGED DATA LEN:", decoded_data[:-1])
	# print(decoded_data)
	t1_decode = (time.time() - t0_decode) * 1000
	print(('[%s] Latency DECODING Payload (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_decode)))

	# test printing
	# print(" ##### decoded_data[-1][0] = ", decoded_data[-1][0])  # tagged_data_len
	# print(" ##### decoded_data[-2][0] = ", decoded_data[-2][0])  # total_number_of_tag
	# print(" ##### decoded_data[-3][0] = ", decoded_data[-3][0])  # t0_part_2
	# print(" ##### decoded_data[-4][0] = ", decoded_data[-4][0])  # t0_part_1
	# print(" ##### decoded_data[-5][0] = ", decoded_data[-5][0])  # drone_id
	# print(" ##### decoded_data[-6][0] = ", decoded_data[-6][0])  # img_data

	# Extract information
	t0_tag_extraction = time.time()
	drone_id = extract_drone_id(decoded_data, encoded_img_len)
	t0 = extract_t0(decoded_data, encoded_img_len)
	# print(" ----- drone_id:", drone_id, type(drone_id))
	# print(" ----- t0:", t0, type(t0))
	t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
	print(('[%s] Latency Tag Extraction (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_tag_extraction)))

	# popping tagged information
	t0_non_img_cleaning = time.time()
	# print(" ----- OLD SHAPE decoded_data:", decoded_data.shape)
	for i in range(extra_tag_len):
		decoded_data = np.delete(decoded_data, -1)
	decoded_data = decoded_data.reshape(decoded_data_len-5, 1)
	# print(" ----- NEWWWW SHAPE decoded_data:", decoded_data.shape)
	# print(" ##### decoded_data[-1][0] = ", decoded_data[-1][0])  # tagged_data_len
	t1_non_img_cleaning = (time.time() - t0_non_img_cleaning) * 1000
	print(('[%s] Latency Non Image Cleaning (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_non_img_cleaning)))

	# extracting (compressed) image information
	t0_img_extraction = time.time()
	extracted_cimg = decoded_data[:-1].copy().astype('uint8')
	t1_img_extraction = (time.time() - t0_img_extraction) * 1000
	print(('[%s] Latency Image Extraction (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_img_extraction)))

	# Image de-compression (restore back into FullHD)
	t0_decompress_img = time.time()
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape)
	deimg_len = list(extracted_cimg.shape)[0]
	# print(" ----- deimg_len:", deimg_len)
	decoded_img = extracted_cimg.reshape(deimg_len, 1)
	# print(" ### SHAPE: decoded_img = ", decoded_img.shape, type(decoded_img), type(decoded_img[0][0]))
	decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
	# print(" ----- SHAPE decompressed_img:", decompressed_img.shape)
	t1_decompress_img = (time.time() - t0_decompress_img) * 1000
	print(('[%s] Latency DE-COMPRESSING IMG (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_decompress_img)))

	cv2.imwrite("decompressed_img.jpg", decompressed_img)

# t0_decode_img = time.time()
	# decoded_img = decoded_data[:-1].copy().astype('uint8')
	# t1_decode_img = (time.time() - t0_decode_img) * 1000
	# print(('\n[%s] Latency GET DECODED IMG (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decode_img)))
	#
	# t0_decompress_img = time.time()
	# # print(" ### SHAPE: decoded_img = ", decoded_img.shape)
	# deimg_len = list(decoded_img.shape)[0]
	# # print(" ----- deimg_len:", deimg_len)
	# decoded_img = decoded_img.reshape(deimg_len, 1)
	# # print(" ### SHAPE: decoded_img = ", decoded_img.shape, type(decoded_img), type(decoded_img[0][0]))
	# decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
	# t1_decompress_img = (time.time() - t0_decompress_img) * 1000
	# print(('\n[%s] Latency DECOMPRESS IMG (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decompress_img)))




	# ############
	# ############ For IMAGE ONLY
	# t0_decoding = time.time()
	# deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
	# print(" === SHAPE deserialized_bytes:", deserialized_bytes.shape)
	# print(deserialized_bytes)
	# t1_decoding = (time.time() - t0_decoding) * 1000
	# print(
	#     ('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	#
	# # t0_decoding = time.time()
	# # deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
	# # print(">>> img_ori SHAPE:", deserialized_img.shape)
	# # t1_decoding = (time.time() - t0_decoding) * 1000
	# # print(
	# #     ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	# ############ END For IMAGE ONLY
	############

	# deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
	# print(" #### deserialized_bytes TYPE:", type(deserialized_bytes), len(deserialized_bytes))
	# print(" - SHAPE: ", deserialized_bytes.shape)

	# decoded_data = consumed_data.payload.decode("utf-8")
	# print(" #### decoded_data TYPE:", type(decoded_data), len(decoded_data))
	# split_data = decoded_data.split(" ")
	# drone_id = split_data[0]
	# t0_data = split_data[1]
	# bytes_img = bytes(split_data[2], encoding='utf8')
	# print(" ### drone_id:", drone_id)
	# print(" ### t0_data:", t0_data)
	# print(" ### bytes_img TYPE:", type(bytes_img), len(bytes_img))
	# # print(decoded_data)
	#
	# print()
	#
	# t1 = time.time()
	# deserialized_bytes = np.frombuffer(bytes_img, dtype=np.int8)
	# print(type(deserialized_bytes))
	# print(" SHAPE deserialized_bytes:", deserialized_bytes.shape)
	# decimg = cv2.imdecode(deserialized_bytes, 1)  # decompress
	# t2 = time.time() - t1
	# print(" ### SHAPE decimg:", decimg.shape)
	# print('\nLatency Decode: (%.2f ms)' % (t2 * 1000))

	# exit()

	# ############
	# ############ For IMAGE ONLY
	# t0_decoding = time.time()
	# deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
	# t1_decoding = (time.time() - t0_decoding) * 1000
	# print(
	#     ('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	#
	# t0_decoding = time.time()
	# deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
	# print(">>> img_ori SHAPE:", deserialized_img.shape)
	# t1_decoding = (time.time() - t0_decoding) * 1000
	# print(
	#     ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	# ############ END For IMAGE ONLY
	# ############

	# time = '(not specified)' if sample.data_info is None or sample.data_info.timestamp is None else datetime.fromtimestamp(
	#     sample.data_info.timestamp.time)
	# print(">> [Subscription listener] Received ('{}': '{}') published at {}"
	#       .format(sample.res_name, sample.payload.decode("utf-8"), time))


# initiate logging
zenoh.init_logger()

print("Openning session...")
session = zenoh.net.open(conf)

print("Declaring Subscriber on '{}'...".format(selector))
sub_info = SubInfo(Reliability.Reliable, SubMode.Push)

sub = session.declare_subscriber(selector, sub_info, listener)

print("Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

sub.undeclare()
session.close()
