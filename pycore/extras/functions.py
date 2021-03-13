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
