#!/usr/bin/env bash 

GEAR=ciso
IMAGE=flywheel/mrr:0.1.1
LOG=mrr-0.1.1-66d9c853738a353afa4f0fe8

# Command:
docker run -it --rm --entrypoint bash\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/app/:/flywheel/v0/app\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/utils:/flywheel/v0/utils\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/run.py:/flywheel/v0/run.py\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/${LOG}/input:/flywheel/v0/input\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/${LOG}/output:/flywheel/v0/output\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/${LOG}/work:/flywheel/v0/work\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/${LOG}/config.json:/flywheel/v0/config.json\
	-v /Users/nbourke/GD/atom/unity/fw-gears/${GEAR}/${LOG}/manifest.json:/flywheel/v0/manifest.json\
	$IMAGE
