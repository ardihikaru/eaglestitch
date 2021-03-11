import cv2
import imutils
from extras.functions import get_current_datetime, create_folder

try:
	from black_region_remover import BlackRegionRemover  # for direct execution
except Exception as e:
	from .black_region_remover import BlackRegionRemover  # for execution via EagleStitch System
import logging

###

L = logging.getLogger(__name__)


###


class Stitch(object):
	"""
        This class perform image stitching by taking two parameters:
        - imgs: list of images (numpy array)
        - batch_num: total number of images to be stitched
    """

	def __init__(self, imgs, batch_num, config):
		# set default value for muttable variable
		"""
		Sample values for `config` variable:
		{
			"root_output_dir": "/path/to/output/root/directory/",
			"store_input_imgs": true,
			"crop": true,
			"source_img_name": "source_imgs",
			"stitched_img_name": "stitched.jpg",
			"crop_stitched_img_name": "crop_stitched.jpg",
		}
		"""

		self.batch_num = batch_num
		self.imgs = imgs
		self.stitch_result = None
		self.stitch_result_dir = None
		self.config = config

	def run(self):
		L.warning("[INFO] I am running stitching now")

		# Perform stitching
		stitching_succeed, stitched_img = self._perform_stitching()

		# create a new folder to store the stitching source and result images
		self._create_result_directory()

		# Store source images (if enabled)
		if self.config.get("store_input_imgs"):
			self._store_source_imgs()

		# generate stitched image path
		stitched_img_path = self._generate_stitched_img_path(stitched_img)

		# Store `stitched_img` and source images to disk if stitching succeed
		if stitching_succeed:
			# Store stitched image
			cv2.imwrite(stitched_img_path, stitched_img)

			# Cropped and store stitched image (if enabled)
			if self.config.get("crop"):
				self._crop_and_store_stitched_img(stitched_img)

		# save stitching result
		self.stitch_result = {
			"stitching_status": stitching_succeed,
			"stitched_img_path": stitched_img_path
		}

	def _crop_and_store_stitched_img(self, stitched_img):
		# Remove black region
		black_region_remover = BlackRegionRemover(stitched_img)
		black_region_remover.remove_black_region()
		_clean_stitched_img = black_region_remover.get_cropped_img()

		# generate stitched image path
		clean_stitched_img_path = self._generate_cropped_stitched_img_path()

		# Store clean stitched image
		cv2.imwrite(clean_stitched_img_path, _clean_stitched_img)

		return black_region_remover.get_cropped_img()

	def _store_source_imgs(self):
		_idx = 0
		for img in self.imgs:
			_idx += 1
			# generate image name
			_img_name = "source_img_{}".format(str(_idx))
			_store_target_path = "{}/{}/{}.jpg".format(
				self.stitch_result_dir,
				self.config.get("source_img_name"),
				_img_name
			)

			# Store this source image
			cv2.imwrite(_store_target_path, img)
		pass

	def _create_result_directory(self):
		# generate output name
		_output_folder_name = get_current_datetime(is_folder=True)

		# generate output path
		self.stitch_result_dir = "{}{}".format(self.config.get("root_output_dir"), _output_folder_name)

		# create root output folder if not exist yet
		create_folder(self.stitch_result_dir)

		# create source folder (if enabled)
		if self.config.get("store_input_imgs"):
			_source_folder_path = "{}/{}".format(self.stitch_result_dir, self.config.get("source_img_name"))
			create_folder(_source_folder_path)

	def _generate_cropped_stitched_img_path(self):
		_cropped_stitched_img_name = self.config.get("crop_stitched_img_name")
		cropped_stitched_img_path = "{}/{}".format(self.stitch_result_dir, _cropped_stitched_img_name)
		return cropped_stitched_img_path

	def _generate_stitched_img_path(self, stitched_img):
		if stitched_img is None:
			return None
		else:
			_stitched_img_name = self.config.get("stitched_img_name")
			stitched_img_path = "{}/{}".format(self.stitch_result_dir, _stitched_img_name)
			return stitched_img_path

	def _perform_stitching(self):
		""" OpenCV Stitcher """
		# Initialize OpenCV stitcher object
		if imutils.is_cv3():
			cv_stitcher = cv2.createStitcher()
		else:
			cv_stitcher = cv2.Stitcher_create()

		# Perform image stitching
		(stitching_error, stitched_img) = cv_stitcher.stitch(self.imgs)

		stitching_succeed = True if stitching_error == 0 else False
		return stitching_succeed, stitched_img

	def get_stitch_result(self):
		return self.stitch_result


"""
#####

from imutils import paths

L.warning('[INFO] I am loading images ...')

# source_path = './data/pano-5/'
source_path = '/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/pano-5/'
img_source = sorted(list(paths.list_images(source_path)))

_batch_num = 0
_imgs = []

for an_img in img_source:
	img_temp = cv2.imread(an_img)
	_imgs.append(img_temp)
	_batch_num = _batch_num + 1

# config; in the system, it captures config from `*.conf` file
_config = {
	"root_output_dir": "/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/results/",
	"store_input_imgs": True,
	"crop": True,
	"source_img_name": "source_imgs",
	"stitched_img_name": "stitched.jpg",
	"crop_stitched_img_name": "crop_stitched.jpg",
}

stitcher = Stitch(
	imgs=_imgs,
	batch_num=_batch_num,
	config=_config
)

stitcher.run()

_results = stitcher.get_stitch_result()

#####
"""
