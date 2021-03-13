import asab
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
		self.webview_svc = app.get_service("eaglestitch.WebviewerService")

		# static path name
		self.static_path_name = asab.Config["eaglestitch:rest"]["static_path_name"]

		aiohttp_jinja2.setup(
			app.RESTWebContainer.WebApp,
			loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
		)

		_static_path = os.path.join(os.getcwd(), "data/results/")
		app.RESTWebContainer.WebApp['static_root_url'] = "/{}/".format(self.static_path_name)

		# added static dir
		app.RESTWebContainer.WebApp.router.add_static(
			'/{}/'.format(self.static_path_name), path=_static_path, name='static',
		)

		app.RESTWebContainer.WebApp.router.add_get('/', self.homepage)
		app.RESTWebContainer.WebApp.router.add_get('/webview/{stitch_id}', self.show_stitched_img)

	@aiohttp_jinja2.template("index.html")
	async def homepage(self, request):
		return {}

	@aiohttp_jinja2.template("show_stitch.html")
	async def show_stitched_img(self, request):
		stitch_id = (request.match_info["stitch_id"]).upper()
		if stitch_id is None:
			L.error("`stitch_id` is missing from request.")
			raise aiohttp.web.HTTPNotFound()

		return await self.webview_svc.load_stitching_result(
			stitch_id=stitch_id
		)
