from app.etc.utils import get_current_timestamp
from app.algorithms.feature_matching import FeatureMatching
from app.algorithms.image_matching import ImageMatching
from app.algorithms.bundle_adjustment import BundleAdjustment
from app.algorithms.auto_panorama_straightening import AutomaticPanoramaStraightening
from app.algorithms.gain_compensation import GainCompensation
from app.algorithms.multiband_blending import MultiBandBlending


class EagleStitchApp:
    def __init__(self, opt):
        self.opt = opt

    def run(self):
        print("\n[%s] Eagle Stitching App is running now" % get_current_timestamp())

        sample_input_data = ["simply dummy. I can be anything"]

        # Begin running each process ...
        # ## 1. Feature Matching
        fm = FeatureMatching(self.opt, sample_input_data)
        fm.run()
        fm_results = fm.get_output()
        print("\n[%s] --- fm_results:" % get_current_timestamp(), fm_results)

        # ## 2. Image Matching
        im = ImageMatching(self.opt, fm_results)
        im.run()
        im_results = im.get_output()
        print("\n[%s] --- im_results:" % get_current_timestamp(), im_results)

        # ## 3. Bundle Adjustment
        ba = BundleAdjustment(self.opt, fm_results)
        ba.run()
        ba_results = ba.get_output()
        print("\n[%s] --- ba_results:" % get_current_timestamp(), ba_results)

        # ## 4. Automatic Panorama Straightening
        aps = AutomaticPanoramaStraightening(self.opt, fm_results)
        aps.run()
        aps_results = aps.get_output()
        print("\n[%s] --- aps_results:" % get_current_timestamp(), aps_results)

        # ## 5. Gain Compensation
        gc = GainCompensation(self.opt, fm_results)
        gc.run()
        gc_results = gc.get_output()
        print("\n[%s] --- gc_results:" % get_current_timestamp(), gc_results)

        # ## 6. Multi-Band Blending
        mbb = MultiBandBlending(self.opt, fm_results)
        mbb.run()
        mbb_results = mbb.get_output()
        print("\n[%s] --- mbb_results:" % get_current_timestamp(), mbb_results)
