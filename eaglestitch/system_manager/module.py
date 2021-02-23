import asab
from .service import SystemManagerService
import logging

###

L = logging.getLogger(__name__)


###


class SystemManagerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = SystemManagerService(app)

	async def initialize(self, app):
		L.warning("[System Manager Module] is loaded.")
