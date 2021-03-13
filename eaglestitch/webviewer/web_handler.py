import jinja2
import os
import aiohttp_jinja2
from jinja2 import Environment, FileSystemLoader
import logging

###

L = logging.getLogger(__name__)

###


class WebviewHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		aiohttp_jinja2.setup(
			app.RESTWebContainer.WebApp,
			loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
		)

		app.RESTWebContainer.WebApp.router.add_get('/', self.show_stitched_img)

	@aiohttp_jinja2.template("index.html")
	async def show_stitched_img(self, request):
		return {}
