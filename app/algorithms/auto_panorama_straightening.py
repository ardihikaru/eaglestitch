from app.etc.utils import get_current_timestamp


class AutomaticPanoramaStraightening:
    def __init__(self, opt, input_data):
        self.opt = opt
        self.input_data = input_data
        self.output_data = None

    def run(self):
        print("\n[%s] 4. Running Automatic Panorama Straightening" % get_current_timestamp())

    def get_output(self):
        return self.output_data
