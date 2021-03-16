from enum import Enum


class ConfigurableVars(Enum):
	PROCESSOR_STATUS = "processor_status"
	STITCHING_MODE = "stitching_mode"
	TARGET_STITCH = "target_stitch"
	FRAME_SKIP = "frame_skip"
	MAX_FRAMES = "max_frames"


class StitchingMode(Enum):
	BATCH = 1
	FULL = 2
