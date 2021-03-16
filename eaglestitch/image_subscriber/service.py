import asab
import asyncio
import time
import numpy as np
from datetime import datetime
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging
from configurable_vars.configurable_vars import ConfigurableVars, StitchingMode
from concurrent.futures import ThreadPoolExecutor

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

	def __init__(self, app, service_name="eaglestitch.ImageSubscriberService"):
		super().__init__(app, service_name)

		# load services
		self.System_manager = app.get_service('eaglestitch.SystemManagerService')
		self.stitching_svc = app.get_service("eaglestitch.StitchingService")

		# stitching mode
		self._stitching_mode = asab.Config["stitching:config"].getint("mode")

		# config for Stitching mode = 1 (BATCH)
		self.target_stitch = asab.Config["stitching:config"].getint("target_stitch")

		# config for Stitching mode = 1 (FULL)
		self.frame_skip = asab.Config["stitching:config"].getint("frame_skip")
		self.max_frames = asab.Config["stitching:config"].getint("max_frames")
		self.frame_skip_counter = 0
		self.enqueued_frames = 0

		self.batch_num = 0  # we will reset this value once finished sending tuple of imgs into stitching service
		self.batch_imgs = []  # we will reset this value once finished sending tuple of imgs into stitching service
		# input and target stitched image resolution
		self.img_w = asab.Config["stitching:config"].getint("img_w")
		self.img_h = asab.Config["stitching:config"].getint("img_h")
		self.img_ch = asab.Config["stitching:config"].getint("img_ch")

		self.pubsub_mode = asab.Config["pubsub:config"]["mode"]

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
			StitchingMode.FULL.value
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
		# skip frames (if enabled)
		# append current captured img data
		if self.batch_num == 1 or (0 < self.frame_skip == self.frame_skip_counter):
			self.batch_imgs.append(img_info["img"])
			self.enqueued_frames += 1
			self.frame_skip_counter = 0  # reset skip counter

		else:
			self.frame_skip_counter += 1

		# when max_frames == 0 or (max_frames > 0 and total number of enqueued frames >= max_frames),
		# close the pool and start the stitching pipeline
		if self.max_frames == 0 or (self.max_frames != 0 and self.enqueued_frames == self.max_frames):
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

			# Force stop the stitching processor
			self._processor_status = False

	def img_listener(self, consumed_data):
		self.batch_num += 1

		# For debugging only; please comment it once done the debugging session
		# print(" ######### self.batch_num = ", self.batch_num)

		# ####################### For tuple data
		t0_decoding = time.time()
		img_total_size = self.img_w * self.img_h * self.img_ch
		encoder_format = [
			('id', 'U10'),
			('timestamp', 'f'),
			('data', [('flatten', 'i')], (1, img_total_size)),
			('store_enabled', '?'),
		]
		deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=encoder_format)

		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('\n[ZENOH CONSUMER][%s] Latency img_info (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		t0_decoding = time.time()

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
		################################

		# Check Stitching mode
		# if disabled (false), simply do nothing and make sure to empty any related variables
		if not self._processor_status:
			L.warning("[ZENOH CONSUMER] I AM DOING NOTHING AT THE MOMENT")
			# Always empty any related variables
			self.batch_num = 0
			self.batch_imgs = []
			self.frame_skip_counter = 0
			self.enqueued_frames = 0
		if self._processor_status and self._stitching_mode == StitchingMode.BATCH.value:
			# Batch mode
			# It will enqueue up to `target_stitch` frames and do stitching each
			self.__exec_stitching_in_batch_mode(img_info)

			# Full mode
			# It will enqueue all captured images (except skipped frames and/or hard limited) and do stitching only ONCE
		elif self._processor_status and self._stitching_mode == StitchingMode.FULL.value:
			self.__exec_stitching_in_full_mode(img_info)

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
