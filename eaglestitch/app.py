#!/usr/bin/env python3

import asab
import asab.web
import asab.web.rest
import asab.storage
import logging

from .stitching_api import StitchingAPIModule

###

L = logging.getLogger(__name__)

###


class EagleStitchApplication(asab.Application):

	def __init__(self):
		super().__init__()

		# Web module/service
		self.add_module(asab.web.Module)
		websvc = self.get_service('asab.WebService')

		# Create a dedicated web container
		self.RESTWebContainer = asab.web.WebContainer(websvc, 'eaglestitch:rest')
		# JSON exception middleware
		self.RESTWebContainer.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		# Modules
		self.add_module(StitchingAPIModule)

	async def initialize(self):
		L.warning("EagleStitch System is running!")
