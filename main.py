from __future__ import division
import argparse
from app.eagle_stitch_app import EagleStitchApp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--enable-cv-out', dest='cv_out', action='store_true', help="Enable/disable CV Out results")

    opt = parser.parse_args()
    print(opt)

    EagleStitchApp(opt).run()
