import asab
import logging

###

L = logging.getLogger(__name__)


###


class WebviewerService(asab.Service):

	def __init__(self, app, service_name="eaglestitch.WebviewerService"):
		super().__init__(app, service_name)
