import asab
from .service import StitchingService
import logging

###

L = logging.getLogger(__name__)


###


class StitchingModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = StitchingService(app)

	async def initialize(self, app):
		L.warning("[SYSTEM PREPARATION] Stitching Module module is loaded.")
