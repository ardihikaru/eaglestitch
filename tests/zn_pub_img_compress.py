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

t0_compress_img = time.time()
# t0_decoding = time.time()
result, imgencode = cv2.imencode('.jpg', frame, encode_param)
img_len, _ = imgencode.shape
t1_compress_img = (time.time() - t0_compress_img) * 1000
print(('\n[%s] Latency COMPRESS IMG (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_compress_img)))

ori_imgencode = imgencode.copy()

print(" ----- TYPE(imgencode)", type(imgencode), imgencode.shape)
print(" ##### imgencode[0][0] = ", imgencode[0][0])
print(" ##### imgencode[1][0] = ", imgencode[1][0])
print(" ##### imgencode[2][0] = ", imgencode[2][0])
print(" ##### imgencode[-1][0] = ", imgencode[-1][0])
print(" ##### imgencode[img_len-1][0] = ", imgencode[img_len-1][0])
# imgencode[img_len][0] = 1234
# imgencode.append(1)

t0 = str(time.time())
t0_array = t0.split(".")
print(" --- t0_array:", t0_array)
bytes_t0 = b"kucing"
time_buf = np.frombuffer(bytes_t0, dtype=np.uint8)
print(" %%%% time_buf:", time_buf)


def encrypt_str(str_val, byteorder="little"):
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val


def decrypt_str(int_val, byteorder="little"):
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


print()
# Generate int-based drone ID
# int_drone_id = encrypt_str("D01")
int_drone_id = encrypt_str("Drone 01")
int_t0 = encrypt_str(str(time.time()))
print(" ## int_drone_id:", int_drone_id, type(int_drone_id))
print(" ## int_t0:", int_t0)
extra_len = 5
str_drone_id = decrypt_str(int_drone_id)
print(" ## str_drone_id:", str_drone_id, type(str_drone_id))

tagged_data_len = img_len + extra_len

# Generate int-based timestamp

# mystring = "Welcome to the InterStar cafe, serving you since 2412!"
# mystring = t0
# mybytes = mystring.encode('utf-8')
# myint = int.from_bytes(mybytes, 'little')  # byteorder must be either 'little' or 'big'
# print(" ~~~~ myint:", myint)
# recoveredbytes = myint.to_bytes((myint.bit_length() + 7) // 8, 'little')  # byteorder must be either 'little' or 'big'
# recoveredstring = recoveredbytes.decode('utf-8')
# print(" ~~~~ recoveredstring:", recoveredstring)
# print()

# print(" @@@@@@@ t0 =", t0)
# newrow = [[2]]
# newrow = [[myint]]
# newrow = [[12345677854353445366]]  # max 20 digit
# newrow = [[1234567785435345555]]  # max 19 digit
# newrow = [[int_t0]]  # max 19 digit
newrow = [
	[int_drone_id],
	[int(t0_array[0])],
	[int(t0_array[1])],
	[extra_len],
	[tagged_data_len],
]  # max 19 digit
print(" ----- OLD SHAPE imgencode:", imgencode.shape)
imgencode = np.vstack([imgencode, newrow])
print(" ##### imgencode[img_len][0] = ", imgencode[img_len][0])
# sub_arr = imgencode[:-1].copy()
# print(" ----- NEW TYPE(sub_arr)", type(sub_arr), sub_arr.shape)

print(" ----- NEW SHAPE imgencode:", imgencode.shape)

# print(" ##### imgencode[0][1] = ", imgencode[0][1])  # ERROR PASTI
# imgencode = np.vstack((imgencode, [[2][2]]))
# coba = [[2], [2], [2]]
# coba = np.asarray(coba)
# coba2 = imgencode + coba
print("###### img_len:", img_len)
# imgencode[2][0]
# coba = np.append(11111111111111112224444, imgencode)
# print(" ----- SHAPE coba:", coba.shape, coba)
print(" ----- NEW TYPE(imgencode)", type(imgencode), imgencode.shape)

# # bytes_img = imgencode.tobytes()
# bytes_img = sub_arr.tobytes()
# decoded_flatten_img = np.frombuffer(bytes_img, dtype=np.int8)
# print(" ----- NEW TYPE(decoded_flatten_img)", type(decoded_flatten_img), decoded_flatten_img.shape)
# decimg = cv2.imdecode(decoded_flatten_img, 1)  # decompress
# print(" ----- NEW TYPE(decoded_img)", type(decimg), decimg.shape)
# cv2.imwrite("hasil.jpg", decimg)
# cv2.imwrite("input.jpg", frame)
# print(" **** DONE ****")

t0_encoding = time.time()
# tagged_data = np.array(sub_arr, dtype=encoder_format)
# tagged_data = np.array(imgencode, dtype=encoder_format)
# tagged_data = np.array(_val, dtype=encoder_format)
# tagged_data = np.array(_val, dtype=np.int64)
# tagged_data = np.array(imgencode, dtype=np.int64)
# encoded_data = tagged_data.tobytes()
encoded_data = imgencode.tobytes()
t1_encoding = (time.time() - t0_encoding) * 1000
print(('\n[%s] Latency encoding to bytes (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_encoding)))

# arr = np.array([1, 2, 3, 4, 5, 6])
# ts = sub_arr.tobytes()
t0_decode = time.time()
decoded_data = np.frombuffer(encoded_data, dtype=np.int64)
# decoded_data = np.frombuffer(encoded_data, dtype=np.uint64)
# print(decoded_data)
t1_decode = (time.time() - t0_decode) * 1000
print(('\n[%s] Latency DECODING (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decode)))

t0_decode_img = time.time()
decoded_img = decoded_data[:-1].copy().astype('uint8')
t1_decode_img = (time.time() - t0_decode_img) * 1000
print(('\n[%s] Latency GET DECODED IMG (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decode_img)))

t0_decompress_img = time.time()
# print(" ### SHAPE: decoded_img = ", decoded_img.shape)
deimg_len = list(decoded_img.shape)[0]
print(" ----- deimg_len:", deimg_len)
decoded_img = decoded_img.reshape(deimg_len, 1)
# print(" ### SHAPE: decoded_img = ", decoded_img.shape, type(decoded_img), type(decoded_img[0][0]))
decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
t1_decompress_img = (time.time() - t0_decompress_img) * 1000
print(('\n[%s] Latency DECOMPRESS IMG (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decompress_img)))

# print(" ### SHAPE: ori_imgencode = ", ori_imgencode.shape, type(ori_imgencode), type(ori_imgencode[0][0]))
# print(ori_imgencode)
# print(decompressed_img)
# decompressed_img_ori = cv2.imdecode(ori_imgencode, 1)  # decompress
# print(" ### SHAPE: decompressed_img = ", decompressed_img.shape)
# print(" ### SHAPE: decompressed_img_ori = ", decompressed_img_ori.shape)

# cv2.imwrite("decompressed_img.jpg", decompressed_img)
# cv2.imwrite("decompressed_img_ori.jpg", decompressed_img_ori)

# print(np.frombuffer(encoded_data, dtype=int))
# print(np.frombuffer(encoded_data, dtype=encoder_format))
# print(np.frombuffer(_val, dtype=encoder_format))
# print(np.frombuffer(_val, dtype=np.int64))


# print(" ----- TYPE(coba)", type(coba), coba.shape)
# coba2 = np.asarray(coba, dtype=np.int8)
# print(" ----- SHAPE coba2:", coba2.shape, coba2)


# result, imgencode = cv2.imencode('.png', frame, encode_param)
# data = np.array(imgencode)
# print(" ----- TYPE(data)", type(data))
# print(" SHAPE data:", data.shape)
# t1_decoding = (time.time() - t0_decoding) * 1000
# print(('\n[%s] Latency imgencode (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
#
# t0_decoding = time.time()
# # stringData = data.tostring()
# # print(" ---- TYPE:", type(stringData))
# encoded_data = data.tobytes()
# # bytes_data = bytes(stringData, encoding='utf8')
# # buf = "[{:4d}] {}".format(1, encoded_data)
# # buf = "[{:4d}] {}".format(1, stringData)
# # bytes_data = bytes(buf, encoding='utf8')
# # print(buf)
# t1_decoding = (time.time() - t0_decoding) * 1000
# print(('\n[%s] Latency tostring (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
# print(" ---- STRING len stringData: ", len(encoded_data))
#
# # val = [('Drone_1', time.time(), imgencode.tobytes())]
# buf = "{} {} {}".format('Drone_1', time.time(), encoded_data)
#
for idx in itertools.count():
	# time.sleep(0.33)
	time.sleep(1.33)
	# buf = "[{:4d}] {}".format(idx, value)
	# buf = "[{:4d}] {}".format(idx, stringData)
	# print(" --- sending Bytes image..")
	# print("[{}] Writing Data ('{}': '{}')...".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), rid, buf))
	# session.write(rid, bytes(buf, encoding='utf8'))
	# session.write(rid, encoded_data)
	# session.write(rid, bytes_data)
	# session.write(rid, stringData)
	session.write(rid, encoded_data)
	# session.write(rid, imgencode.tobytes())
#
# publisher.undeclare()
# session.close()
