#!/usr/bin/env python
from typing import List
import string, os, sys
import re
import shutil
from typing import Tuple
from flywheel_gear_toolkit import GearToolkitContext

#### define various pathes to software packages
def beta_triplane_SRImageReconViaANTS(gear_inputs: dict, gear_options: dict, app_options: dict,) -> List[str]:
	gear_context: GearToolkitContext
	### age matched version of the MNI template - HeadTemplate includes the skull, Template is skull stipped
	targetTemplate = app_options.get("target_template")
	Template = os.path.join("/flywheel/v0/app/templates/", targetTemplate) 
	#print("template is: ", Template)

	### path to ANTS bin director
	antsTemplateBuilder = "antsMultivariateTemplateConstruction2.sh -d 3 -i 15 -j 4  -t SyN -m MI -z /flywheel/v0/app/templates/"+Template+" -o "
	print("ants command is: ", antsTemplateBuilder)

	### a simple script that just sets the image dimensions
	resetImageDimsions = "resetImageDimensions"
	# ??? IS THIS A SCRIPT SOMEWHERE ???

	# determine the data-containing directories
	rawDataDirectory = '/flywheel/v0/input/'
	dataSubDirectories = []
	for subDir in os.listdir(rawDataDirectory):
		print("mod is: ", subDir)
		try:
			os.rename(gear_inputs[subDir], re.sub(r'[\(\)]', r'', gear_inputs[subDir]))
		except:
			print("Nothing to rename")
			pass

		dirPath = os.path.join(rawDataDirectory, subDir)
		file = os.listdir(dirPath) 
		filePath = os.path.join(dirPath, file[0])
		print("filePath is: ", filePath)
		dst = os.path.join('/flywheel/v0/work/', file[0])
		try:
			shutil.copyfile(filePath, dst)
			print('copied to: ', dst)
		except:
			print("Error occurred while copying file.")

	#### set up the result directory
	volumeReconstructionDirectory = "/flywheel/v0/work"
	if os.path.exists(volumeReconstructionDirectory):
		pass
	else:
		os.system("mkdir "+volumeReconstructionDirectory)


	# ??? REDUNDENT ??
	# # now re-orient the images
	# for file in os.listdir(volumeReconstructionDirectory):
	# 	if file.find(".nii")>0 or file.find(".gz")<0:
	# 		print(file)
	# 		os.system("fslchfiletype NIFTI_GZ "+volumeReconstructionDirectory+"/"+file)
	# 		os.system("fslcpgeom "+Template+" "+volumeReconstructionDirectory+"/"+file+" -d ")
			
	# now we need to reset the orientation labels
	for file in os.listdir(volumeReconstructionDirectory):
		print(file)
		if file.find("COR")>=0:
			swap = " x -z y "
		elif file.find("SAG")>=0:
			swap = " z -x y "
		else:
			swap = "x y z "
		
		os.system("fslswapdim "+volumeReconstructionDirectory+"/"+file+" "+swap+" "+volumeReconstructionDirectory+"/"+file)
		os.system("fslcpgeom "+Template+" "+volumeReconstructionDirectory+"/"+file+" -d ")
		#os.system("fslchfiletype NIFTI "+volumeReconstructionDirectory+"/"+file)
		
	# reset the image dimensions
	imagesForVolumeReconstruction = []
	for file in os.listdir(volumeReconstructionDirectory):
		if file.find("nii")>=0: 
			if file.find("AXI")>=0:
				imageDimensions = " 1.5 1.5 5 "
			elif file.find("COR")>=0:
				imageDimensions = " 1.5 5 1.5 "
			elif file.find("SAG")>=0:
				imageDimensions = " 5 1.5 1.5 "
			else:
				imageDimensions = " 1.5 1.5 1.5 "
			
			fileplit = file.split(".nii")
			newfile = fileplit[0]+"_reshaped.nii"
				
			print(volumeReconstructionDirectory+"/"+file+" "+volumeReconstructionDirectory+"/"+newfile+" "+imageDimensions)
			
			# What is resetImageDimsions??
			#os.system(resetImageDimsions+" "+volumeReconstructionDirectory+"/"+file+" "+volumeReconstructionDirectory+"/"+newfile+" "+imageDimensions)
			
			if file.find("T2")>=0 and file.find(".nii")>=0:
				imagesForVolumeReconstruction.append(volumeReconstructionDirectory+"/"+newfile)
		
	### combine the images into the high resolution isotropic volume and calculate all the individual warp transforms
	# reconstruct the isotropic volume
	reconstructionCommand = antsTemplateBuilder+" "+volumeReconstructionDirectory+"/reconstructedVolume "
	for i in imagesForVolumeReconstruction:
		reconstructionCommand+=i+" "
	print(reconstructionCommand)
	#os.system(reconstructionCommand)
			
			
		

		
		
		
		