import asab
import asyncio
import time
import numpy as np
from datetime import datetime
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging
from configurable_vars.configurable_vars import ConfigurableVars, StitchingMode, ActionMode
from extras.functions import decrypt_str, extract_drone_id, extract_t0
from concurrent.futures import ThreadPoolExecutor
import cv2

###

L = logging.getLogger(__name__)


###


class ImageSubscriberService(asab.Service):

	class ErrorCode(object):
		ERR_ZENOH_MODE = "system_err_001"
		ERR_ZENOH_SUBSCRIPTION = "system_err_002"
		ERR_REDIS_MODE = "system_err_003"
		ERR_SUBSCRIPTION_SELECTOR = "system_err_004"
		ERR_STITCHING_MODE = "system_err_005"

	class PubSubMode(object):
		ZENOH = "zenoh"
		REDIS = "redis"

	class ZenohConsumerType(object):
		NON_COMPRESSION_TAGGED_IMAGE = 3
		COMPRESSION_TAGGED_IMAGE = 4

	def __init__(self, app, service_name="eaglestitch.ImageSubscriberService"):
		super().__init__(app, service_name)

		# load services
		self.System_manager = app.get_service('eaglestitch.SystemManagerService')
		self.stitching_svc = app.get_service("eaglestitch.StitchingService")

		# stitching mode
		self._stitching_mode = asab.Config["stitching:config"].getint("mode")

		# config for Stitching mode = 1 (BATCH)
		self.target_stitch = asab.Config["stitching:config"].getint("target_stitch")

		# config for Stitching mode = 2 (FULL)
		self.frame_skip = asab.Config["stitching:config"].getint("frame_skip")
		self.max_frames = asab.Config["stitching:config"].getint("max_frames")
		self.frame_skip_counter = 0
		self.enqueued_frames = 0
		self.forced_stop = False

		self.batch_num = 0  # we will reset this value once finished sending tuple of imgs into stitching service
		self.batch_imgs = []  # we will reset this value once finished sending tuple of imgs into stitching service
		# input and target stitched image resolution
		self.img_w = asab.Config["stitching:config"].getint("img_w")
		self.img_h = asab.Config["stitching:config"].getint("img_h")
		self.img_ch = asab.Config["stitching:config"].getint("img_ch")

		self.pubsub_mode = asab.Config["pubsub:config"]["mode"]
		self.comsumer_type = asab.Config["pubsub:config"].getint("comsumer_type")

		# config zenoh pubsub config
		self.zenoh_comm_protocol = asab.Config["zenoh:config"]["comm_protocol"]
		self.zenoh_comm_ip = asab.Config["zenoh:config"]["comm_ip"]
		self.zenoh_comm_port = asab.Config["zenoh:config"]["comm_port"]
		self.selector = asab.Config["zenoh:config"]["selector"]
		self.listener = "{}/{}:{}".format(
			self.zenoh_comm_protocol,
			self.zenoh_comm_ip,
			self.zenoh_comm_port,
		)
		self.sub_svc = None
		self.subscriber = None

		# Load Stitching Manager Consumer
		self.App.PubSub.subscribe("eaglestitch.StitchingManagerPubSub.message!", self._on_pubsub_stitching_manager)

		# set stitching processor status: enabled (true) by default
		self._processor_status = asab.Config["stitching:config"].getboolean("processor")

		# Show WARNING to the log if the processor is DISABLED on load system
		if not self._processor_status:
			L.warning(">>> [IMPORTANT] Stitching Processor is DISABLED On load system <<<")

	async def _on_pubsub_stitching_manager(self, event_type, config):
		"""
		This function simply disable or enable stitching processor
		:param event_type: `event_type` value is `eaglestitch.StoragePubSub.message!`
		:param enable_processor: an action to start or stop the stitching processor
		:return:
		"""

		# WARNING! Prevent on changing variable when Stitching is currently Enabled
		# `processor_status` should be disabled first
		if not self._processor_status and ConfigurableVars.STITCHING_MODE.value in config:
			self._stitching_mode = config[ConfigurableVars.STITCHING_MODE.value]
		if not self._processor_status and ConfigurableVars.TARGET_STITCH.value in config:
			self.target_stitch = config[ConfigurableVars.TARGET_STITCH.value]
		if not self._processor_status and ConfigurableVars.FRAME_SKIP.value in config:
			self.frame_skip = config[ConfigurableVars.FRAME_SKIP.value]
		if not self._processor_status and ConfigurableVars.MAX_FRAMES.value in config:
			self.max_frames = config[ConfigurableVars.MAX_FRAMES.value]

		# Check if user requests to stop the stitching through an API
		if config["action_mode"] == ActionMode.START_STOP:
			self.forced_stop = config["forced_stop"]

		# check each configurable vars
		if ConfigurableVars.PROCESSOR_STATUS.value in config:
			self._processor_status = config[ConfigurableVars.PROCESSOR_STATUS.value]

	async def initialize(self, app):
		# validate PubSub and Stitching mode
		if await self._validate_pubsub_mode() and await self._validate_stitching_mode():
			await self.subscription()

	async def _validate_pubsub_mode(self):
		_valid_mode = frozenset([
			self.PubSubMode.ZENOH,
			self.PubSubMode.REDIS
		])
		if self.pubsub_mode not in _valid_mode:
			_err_msg = ">>>>> Invalid PubSub mode; Available mode: `zenoh` and `redis`"
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_ZENOH_MODE,
				system_message=_err_msg
			)

			return False

		return True

	async def _validate_stitching_mode(self):
		_valid_mode = frozenset([
			StitchingMode.BATCH.value,
			StitchingMode.STREAM.value
		])
		if self._stitching_mode not in _valid_mode:
			_err_msg = ">>>>> Invalid Stitching mode; Available mode: `1` (BATCH; default) and `2` (FULL)"
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_STITCHING_MODE,
				system_message=_err_msg
			)

			return False

		return True

	def __exec_stitching_in_batch_mode(self, img_info):
		# append current captured img data
		self.batch_imgs.append(img_info["img"])

		# when N number of images has been collected, send the tuple of images into stitching service
		if self.batch_num == self.target_stitch:
			# Send this tuple of imgs into stitching
			try:
				if not self.stitching_svc.stitch(self.batch_imgs, self.batch_num):
					L.error("Stitching failed")
			except Exception as e:
				L.error("[ZENOH CONSUMER] Stitching pipiline failed. Reason: {}".format(e))

			# Reset the value
			self.batch_num = 0
			self.batch_imgs = []

	def __exec_stitching_in_full_mode(self, img_info):
		# Ignore this process if this function is called due to it a STOP action!
		if not self.forced_stop:
			# skip frames (if enabled)
			# append current captured img data
			if self.batch_num == 1 or (0 < self.frame_skip == self.frame_skip_counter):
				self.batch_imgs.append(img_info["img"])
				self.enqueued_frames += 1
				self.frame_skip_counter = 0  # reset skip counter

			else:
				self.frame_skip_counter += 1

		# close the pool and start the stitching pipeline
		if (self.max_frames == 0 and self.forced_stop) or \
				(self.max_frames != 0 and self.enqueued_frames == self.max_frames):
			# Send this tuple of imgs into stitching
			try:
				if not self.stitching_svc.stitch(self.batch_imgs, self.enqueued_frames):
					L.error("Stitching failed")
			except Exception as e:
				L.error("[ZENOH CONSUMER] Stitching pipiline failed. Reason: {}".format(e))

			# Reset the value
			self.batch_num = 0
			self.batch_imgs = []
			self.frame_skip_counter = 0
			self.enqueued_frames = 0
			self.forced_stop = False

			# Force stop the stitching processor
			self._processor_status = False

	# Deprecated: no more tested!
	def _extract_non_compression_tagged_img(self, consumed_data):

		# ####################### For tuple data
		t0_decoding = time.time()
		img_total_size = self.img_w * self.img_h * self.img_ch
		encoder_format = [
			('id', 'U10'),
			('timestamp', 'f'),
			# ('data', [('flatten', 'i')], (1, img_total_size)),
			# ('data', [('flatten', 'i')], (247142, 1)),
			# ('data', 'U10'),
			# ('data', 'a'),
			# ('data', 'object'),
			# ('data', 'a25'),
			('data', 'U25'),
			# ('store_enabled', '?'),
		]
		deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=encoder_format)
		# deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=object)

		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('\n[ZENOH CONSUMER][%s] Latency img_info (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		t0_decoding = time.time()

		print(" ### DISINI ...")
		t1 = time.time()
		# flatten_img = deserialized_bytes["data"]["flatten"][0]
		flatten_img = np.frombuffer(deserialized_bytes["data"][0], dtype=np.int8)
		print(" ### SHAPE flatten_img:", flatten_img.shape)
		# flatten_img =
		print(" ### len flatten_img:", len(flatten_img), type(flatten_img))
		decimg = cv2.imdecode(flatten_img, 1)  # decompress
		t2 = time.time() - t1
		print(" ### SHAPE decimg:", decimg.shape)
		print('\nLatency Decode: (%.2f ms)' % (t2 * 1000))
		cv2.imwrite("hasil.jpg", stitched_img)

		# decode data
		img_info = {
			"id": str(deserialized_bytes["id"][0]),
			# "img": deserialized_bytes["data"]["flatten"][0].reshape(self.img_h, self.img_w, self.img_ch).astype(
			"img": deserialized_bytes["data"]["flatten"][0].reshape(self.img_w, self.img_h, self.img_ch).astype(
				"uint8"),
			"timestamp": float(deserialized_bytes["timestamp"][0]),
			"store_enabled": bool(deserialized_bytes["store_enabled"][0]),
		}

		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('\n[ZENOH CONSUMER][%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
		###############################

		return img_info

	def _extract_compression_tagged_img(self, consumed_data):

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
		# print(" ##### decoded_data[-1][0] (tagged_data_len) = ", decoded_data[-1][0])  # tagged_data_len
		# print(" ##### decoded_data[-2][0] (total_number_of_tag) = ", decoded_data[-2][0])  # total_number_of_tag
		# print(" ##### decoded_data[-3][0] (t0_part_2) = ", decoded_data[-3][0])  # t0_part_2
		# print(" ##### decoded_data[-4][0] (t0_part_1) = ", decoded_data[-4][0])  # t0_part_1
		# print(" ##### decoded_data[-5][0] (drone_id) = ", decoded_data[-5][0])  # drone_id
		# print(" ##### decoded_data[-6][0] (img_data) = ", decoded_data[-6][0])  # img_data

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
		decoded_data = decoded_data.reshape(decoded_data_len - 5, 1)
		# print(" ----- NEWWWW SHAPE decoded_data:", decoded_data.shape)
		# print(" ##### decoded_data[-1][0] = ", decoded_data[-1][0])  # tagged_data_len
		t1_non_img_cleaning = (time.time() - t0_non_img_cleaning) * 1000
		print(
			('[%s] Latency Non Image Cleaning (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_non_img_cleaning)))

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

		# cv2.imwrite("decompressed_img.jpg", decompressed_img)
		# cv2.imwrite("decompressed_img_{}.jpg".format(str(t0_decompress_img)), decompressed_img)

		img_info = None
		return img_info

	def img_listener(self, consumed_data):
		self.batch_num += 1

		# For debugging only; please comment it once done the debugging session
		# print(" ######### self.batch_num = ", self.batch_num)
		print(" ######### self.comsumer_type = ", self.comsumer_type)

		if self.comsumer_type == self.ZenohConsumerType.NON_COMPRESSION_TAGGED_IMAGE:
			img_info = self._extract_non_compression_tagged_img(consumed_data)
		elif self.comsumer_type == self.ZenohConsumerType.COMPRESSION_TAGGED_IMAGE:
			img_info = self._extract_compression_tagged_img(consumed_data)
		else:
			_err_msg = ">>>>> [ZENOH Consumer] Invalid Zenoh consumer type"
			L.error(_err_msg)
			exit(0)  # Force stop the system!

		# For debugging purpose..
		exit(0)  # Force stop the system!

		# # Check Stitching mode
		# # if disabled (false), simply do nothing and make sure to empty any related variables
		# if not self._processor_status and not self.forced_stop:
		# 	L.warning("[ZENOH CONSUMER] I AM DOING NOTHING AT THE MOMENT")
		# 	# Always empty any related variables
		# 	self.batch_num = 0
		# 	self.batch_imgs = []
		# 	self.frame_skip_counter = 0
		# 	self.enqueued_frames = 0
		# if self._processor_status and self._stitching_mode == StitchingMode.BATCH.value:
		# 	# Batch mode
		# 	# It will enqueue up to `target_stitch` frames and do stitching each
		# 	self.__exec_stitching_in_batch_mode(img_info)
		#
		# elif self._processor_status and self._stitching_mode == StitchingMode.STREAM.value:
		# 	# Full mode
		# 	# It will enqueue all captured images (except skipped frames and/or hard limited) and do stitching only ONCE
		# 	self.__exec_stitching_in_full_mode(img_info)
		#
		# # Finalize and start the stitching pipeline
		# elif not self._processor_status and self._stitching_mode == StitchingMode.STREAM.value:
		# 	self.__exec_stitching_in_full_mode(img_info)

	def _start_zenoh(self):
		self.sub_svc = ZenohNetSubscriber(
			_selector=self.selector, _session_type="SUBSCRIBER", _listener=self.listener
		)
		self.sub_svc.init_connection()

		self.sub_svc.register(self.img_listener)
		self.subscriber = self.sub_svc.get_subscriber()

	# once module stopped, stop the subscription
	async def finalize(self, app):
		await self._stop_subscription()

	async def _start_zenoh_subscription(self):
		try:
			executor = ThreadPoolExecutor(1)
			executor.submit(self._start_zenoh)
		except Exception as e:
			_err_msg = ">>>>> ZENOH Subscription Failed; Reason: `{}`".format(e)
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_ZENOH_SUBSCRIPTION,
				system_message=_err_msg
			)

	# TODO: implement Redis Subscription
	async def _start_redis_subscription(self):
		_err_msg = ">>>>> REDIS Subscription function is not implemeted yet."
		L.error(_err_msg)
		await self.System_manager.publish_error(
			system_code=self.ErrorCode.ERR_REDIS_MODE,
			system_message=_err_msg
		)

	async def _stop_subscription(self):
		if self.pubsub_mode == self.PubSubMode.ZENOH:
			try:
				self.sub_svc.close_connection(self.subscriber)
			except AttributeError as e:
				pass

	async def subscription(self):
		if self.pubsub_mode == self.PubSubMode.ZENOH:
			await self._start_zenoh_subscription()
		elif self.pubsub_mode == self.PubSubMode.REDIS:
			# TODO: implement mode Redis PubSub
			await self._start_redis_subscription()
		else:
			_err_msg = ">>>>> Subscription failed."
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_SUBSCRIPTION_SELECTOR,
				system_message=_err_msg
			)
