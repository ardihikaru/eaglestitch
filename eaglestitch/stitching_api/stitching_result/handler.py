import asab.web.rest
import aiohttp.web
import logging

###

L = logging.getLogger(__name__)

###


class StitchingResultSectionWebHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		app.RESTWebContainer.WebApp.router.add_get('/stitching', self.get_stitching)
		app.RESTWebContainer.WebApp.router.add_get('/stitching/{stitch_id}', self.get_stitching_by_id)

		self.to_url = asab.Config["eaglestitch:rest"].getboolean("to_url")

	async def get_stitching(self, request):
		status, msg, data = await self.stitching_api_svc.get_stitching_result()

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)

	async def get_stitching_by_id(self, request):
		stitch_id = (request.match_info["stitch_id"]).upper()
		if stitch_id is None:
			L.error("`stitch_id` is missing from request.")
			raise aiohttp.web.HTTPBadRequest()

		status, msg, data = await self.stitching_api_svc.get_stitching_result(
			stitch_id=stitch_id,
			to_url=self.to_url,
		)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)
