import asab
from .service import ImageSubscriberService
import logging

###

L = logging.getLogger(__name__)


###


class ImageSubscriberModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ImageSubscriberService(app)

	async def initialize(self, app):
		L.warning("[SYSTEM PREPARATION] Image Subscriber Module module is loaded.")
