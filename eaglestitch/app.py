#!/usr/bin/env python3

import asab
import asab.web
import asab.web.rest
import asab.storage
import logging

from .system_manager import SystemManagerModule
from .storage import StorageModule
from .stitching_api import StitchingAPIModule
from .webviewer import WebviewerModule
from .stitching import StitchingModule
from .image_subscriber import ImageSubscriberModule

###

L = logging.getLogger(__name__)

###


class EagleStitchApplication(asab.Application):

	def __init__(self):
		super().__init__()

		# Load System Message Consumer
		self.PubSub.subscribe("eaglestitch.SystemPubSub.message!", self._on_pubsub_system)

		# Web module/service
		self.add_module(asab.web.Module)
		websvc = self.get_service('asab.WebService')

		# Loading the storage module
		self.add_module(asab.storage.Module)

		# Create a dedicated web container
		self.RESTWebContainer = asab.web.WebContainer(websvc, 'eaglestitch:rest')
		# JSON exception middleware
		self.RESTWebContainer.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		# Modules
		self.add_module(SystemManagerModule)
		self.add_module(StorageModule)  # please make sure that this module is loaded before any other modules
		self.add_module(StitchingAPIModule)
		self.add_module(WebviewerModule)
		self.add_module(StitchingModule)  # this should be loaded BEFORE `Image Subscriber Module`
		self.add_module(ImageSubscriberModule)

	async def initialize(self):
		L.warning("[SYSTEM] EagleStitch System is running!")

	async def running_subscription(self):
		await self.img_subscriber_svc.subscription()

	async def _on_pubsub_system(self, event_type, sys_message_json):
		"""
		This function acts as the action when any message-related task is consumed
		:param event_type: `event_type` value is `eaglestitch.SystemPubSub.message!`
		:param sys_message_json: a dictionary consists of `code` and `message` keys
		:return:
		"""
		L.error("system_code:`{}`; Message=`{}`\n".format(sys_message_json["code"], sys_message_json["message"]))

		# If "system_err*" in code, it asks to stop the system
		if "system_err" in sys_message_json["code"]:
			self.PubSub.subscribe("Application.tick!", self.exit_with_error)

	async def exit_with_error(self, event_type):
		"""
		This function triggers the system to stop due to an error
		:param event_type: `event_type` value is always `Application.tick!` (from PubSub default functionality)
		:return:
		"""
		self.stop()

	async def finalize(self):
		L.warning("*****[SYSTEM] Eagle Stitch system stopped gracefully.")
