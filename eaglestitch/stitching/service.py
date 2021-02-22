import asab
import logging

###

L = logging.getLogger(__name__)


###


class StitchingService(asab.Service):

	def __init__(self, app, service_name="StitchingService"):
		super().__init__(app, service_name)

	async def stitch(self, collected_imgs):
		# TODO: implement stitching module
		L.warning("PERFORMING STITCHING FOR THIS TUPLE OF IMAGES")
		pass
