import asab.web.rest
import aiohttp.web
from distutils.util import strtobool
import logging
import aiohttp_cors
from extras.cors import CORS_OPTIONS

###

L = logging.getLogger(__name__)

###


class StitchingResultSectionWebHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		# app.RESTWebContainer.WebApp.router.add_get('/stitching', self.get_stitching)
		# app.RESTWebContainer.WebApp.router.add_get('/stitching/{stitch_id}', self.get_stitching_by_id)

		# setup routes
		resources = [
			app.RESTWebContainer.WebApp.router.add_get('/stitching', self.get_stitching),
			app.RESTWebContainer.WebApp.router.add_get('/stitching/{stitch_id}', self.get_stitching_by_id)
		]

		# append cors to each route
		for res in resources:
			self.cors.add(res, CORS_OPTIONS)

	async def get_stitching(self, request):
		params = request.rel_url.query

		# capture `to_url` value
		if params.get("to_url") is None:
			L.warning("`to_url` is missing from request; set default value as `False`")
			_to_url = False
		else:
			_to_url = bool(strtobool(params.get("to_url")))

		status, msg, data = await self.stitching_api_svc.get_stitching_result(to_url=_to_url)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)

	async def get_stitching_by_id(self, request):
		params = request.rel_url.query

		# capture `to_url` value
		if params.get("to_url") is None:
			L.warning("`to_url` is missing from request; set default value as `False`")
			_to_url = False
		else:
			_to_url = bool(strtobool(params.get("to_url")))

		stitch_id = (request.match_info["stitch_id"]).upper()
		if stitch_id is None:
			L.error("`stitch_id` is missing from request.")
			raise aiohttp.web.HTTPBadRequest()

		status, msg, data = await self.stitching_api_svc.get_stitching_result(
			stitch_id=stitch_id,
			to_url=_to_url,
		)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)
