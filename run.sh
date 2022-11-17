#!/usr/bin/env bash 

IMAGE=flywheel/ciso:beta-bash

# Command:
docker run --rm --entrypoint='python /flywheel/v0/run.py'\
	-e FLYWHEEL=/flywheel/v0\
	-e MYENV=my test environment\
	-v /Users/nbourke/My Drive/scratch/CISO/input:/flywheel/v0/input\
	-v /Users/nbourke/My Drive/scratch/CISO/config.json:/flywheel/v0/config.json\
	-v /Users/nbourke/My Drive/scratch/CISO/manifest.json:/flywheel/v0/manifest.json\
	$IMAGE
