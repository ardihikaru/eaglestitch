from eaglestitch.image_subscriber.zenoh_pubsub.core.zenoh_net import ZenohNet
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging
import sys
import time
import numpy as np

###

L = logging.getLogger(__name__)


###


def img_listener(consumed_data):
	print(" ######### @ img_listener ...")
	t0_decoding = time.time()
	deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
	t1_decoding = (time.time() - t0_decoding) * 1000
	L.warning(
	    ('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))


	t0_decoding = time.time()
	deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
	print(">>> img_ori SHAPE:", deserialized_img.shape)
	t1_decoding = (time.time() - t0_decoding) * 1000
	L.warning(
	    ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))


class PubSub(object):
	def __init__(self):
		pass

	def run(self):
		selector = "/demo/**"
		# listener = "tcp/172.18.8.188:7447"
		listener = "tcp/localhost:7447"

		sub = ZenohNetSubscriber(
			_selector=selector, _session_type="SUBSCRIBER", _listener=listener
		)
		sub.init_connection()

		# sub.register()
		sub.register(img_listener)
		# subscriber = sub.get_subscriber()
		subscriber = sub.get_subscriber()
		L.warning("[ZENOH] Press q to stop...")
		c = '\0'
		while c != 'q':
			c = sys.stdin.read(1)

		# # closing Zenoh subscription & session
		sub.close_connection(subscriber)


sub = PubSub()
sub.run()
