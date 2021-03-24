from datetime import datetime
from os import path
import os


def get_current_datetime(is_folder=False):
	if is_folder:
		return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
	else:
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_datetime_ms(is_folder=False):
	if is_folder:
		return datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
	else:
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def create_folder(target_path):
	if not path.exists(target_path):
		os.mkdir(target_path)


def is_img_exist(target_path):
	if path.exists(target_path):
		return True
	else:
		return False


def encrypt_str(str_val, byteorder="little"):
	""" Converts a string value into an integer value """
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val  # max 19 digit


def decrypt_str(int_val, byteorder="little"):
	""" Converts an integer value into a string value """
	decrypted_bytes = int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder)  # byteorder must be either 'little' or 'big'
	decrypted_str = decrypted_bytes.decode('utf-8')
	return decrypted_str


def extract_drone_id(data, img_len):
	""" Extract drone_id captured by Zenoh's Consumer """
	drone_idx = img_len
	return decrypt_str(int(data[drone_idx][0]))


def extract_t0(data, img_len):
	""" Extract timestamp (t0) captured by Zenoh's Consumer """
	to_p1_idx = img_len + 2
	to_p2_idx = img_len + 3

	t0 = "{}.{}".format(
		data[to_p1_idx][0],
		data[to_p2_idx][0],
	)
	return float(t0)
