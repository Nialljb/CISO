#!/usr/bin/env python

import string, os, sys

#### define various pathes to software packages

### age matched version of the MNI template - HeadTemplate includes the skull, Template is skull stipped
Template = ""
HeadTemplate = ""

### path to ANTS bin director
antsTemplateBuilder = "ANTs2.2/bin/ants/bin/Scripts/antsMultivariateTemplateConstruction2.sh  -d 3 -i 15 -c 2 -j 4  -t SyN -m MI -z "+HeadTemplate+" -o "

### a simple script that just sets the image dimensions
resetImageDimsions = "resetImageDimensions"

if len(sys.argv[1:]) < 1:
	print('Correct Usage: python triplane_SRIMageReconViaANTS.py <path to subject data directory> ')
	sys.exit(1)
	

input = sys.argv[1:]
sourceDirectory = input[0]

#### set up the result directory
volumeReconstructionDirectory = sourceDirectory+"volumeReconstruction/"
if os.path.exists(volumeReconstructionDirectory):
	pass
else:
	os.system("mkdir "+volumeReconstructionDirectory)


# determine the data-containing directories
rawDataDirectory = sourceDirectory+"/rawData/"
dataSubDirectories = []
for fileOrDirectory in os.listdir(rawDataDirectory):
	if fileOrDirectory.find("T1_AXI")>=0 or fileOrDirectory.find("T2_AXI")>=0 or fileOrDirectory.find("T2Weighted_")>=0:
		
		path = rawDataDirectory+fileOrDirectory
			
# now re-orient the images
for file in os.listdir(volumeReconstructionDirectory):
	if file.find(".nii")>0 and file.find(".gz")<0:
		
		os.system("fslchfiletype NIFTI_GZ "+volumeReconstructionDirectory+"/"+file)
		os.system("fslcpgeom "+Template+" "+volumeReconstructionDirectory+"/"+file+" -d ")
		
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
	os.system("fslchfiletype NIFTI "+volumeReconstructionDirectory+"/"+file)
	

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
		
		fileSplit = file.split(".nii")
		newfile = fileSplit[0]+"_reshaped.nii"
			
		print(volumeReconstructionDirectory+"/"+file+" "+volumeReconstructionDirectory+"/"+newfile+" "+imageDimensions)
		
		os.system(resetImageDimsions+" "+volumeReconstructionDirectory+"/"+file+" "+volumeReconstructionDirectory+"/"+newfile+" "+imageDimensions)
		
		if file.find("T2")>=0 and file.find(".nii")>=0:
			imagesForVolumeReconstruction.append(volumeReconstructionDirectory+"/"+newfile)
	
### combine the images into the high resolution isotropic volume and calculate all the individual warp transforms
# reconstruct the isotropic volume
reconstructionCommand = antsTemplateBuilder+" "+volumeReconstructionDirectory+"/reconstructedVolume "
for i in imagesForVolumeReconstruction:
	reconstructionCommand+=i+" "
print(reconstructionCommand)
os.system(reconstructionCommand)
		
		
	

	
	
	
	