from app.etc.utils import get_current_timestamp


class FeatureMatching:
    def __init__(self, opt, input_data):
        self.opt = opt
        self.input_data = input_data
        self.output_data = None

    def run(self):
        print("\n[%s] 1. Running Feature Matching" % get_current_timestamp())

        self.output_data = "data"

    def get_output(self):
        return self.output_data
