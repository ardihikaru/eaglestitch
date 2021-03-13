import asab
import asyncio
import time
import numpy as np
from datetime import datetime
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging
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

	class PubSubMode(object):
		ZENOH = "zenoh"
		REDIS = "redis"

	def __init__(self, app, service_name="eaglestitch.ImageSubscriberService"):
		super().__init__(app, service_name)

		# load services
		self.System_manager = app.get_service('eaglestitch.SystemManagerService')
		self.stitching_svc = app.get_service("eaglestitch.StitchingService")

		self.batch_num = 0  # we will reset this value once finished sending tuple of imgs into stitching service
		self.batch_imgs = []  # we will reset this value once finished sending tuple of imgs into stitching service
		self.target_stitch = asab.Config["stitching:config"].getint("target_stitch")
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
		self._processor_status = True

	async def _on_pubsub_stitching_manager(self, event_type, enable_processor):
		"""
		This function simply disable or enable stitching processor
		:param event_type: `event_type` value is `eaglestitch.StoragePubSub.message!`
		:param enable_processor: an action to start or stop the stitching processor
		:return:
		"""
		self._processor_status = enable_processor

	async def initialize(self, app):
		# validate PubSub mode
		if await self._validate_pubsub_mode():
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

		# check stitching processor status
		# if disabled (false), simply do nothing and make sure to empty any related variables
		if not self._processor_status:
			L.warning("[ZENOH CONSUMER] I AM DOING NOTHING AT THE MOMENT")
			# Always empty any related variables
			self.batch_num = 0
			self.batch_imgs = []

		# if enabled, perform the stitching processor
		else:
			# append current captured img data
			self.batch_imgs.append(img_info["img"])

			# when N number of images has been collected, send the tuple of images into stitching service
			if self.batch_num == self.target_stitch:
				# Send this tuple of imgs into stitching
				try:
					if not self.stitching_svc.stitch(self.batch_imgs, self.batch_num):
						L.error("Stitching failed")
				# TODO: If stitching failed, what's the behavior?
				# Maybe nothing to do if FAILED.
				except Exception as e:
					L.error("[ZENOH CONSUMER] Stitching pipiline failed. Reason: {}".format(e))

				# Reset the value
				self.batch_num = 0
				self.batch_imgs = []

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
			self.sub_svc.close_connection(self.subscriber)

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
