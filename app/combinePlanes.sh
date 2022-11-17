#!/bin/bash

# https://wiki.mouseimaging.ca/display/MICePub/Image+registration+and+ANTs+tools


# inputs
echo "source is ${1}"
echo "sub is ${2}"
echo "ses is ${3}"

input=${1}/${2}/${3}/anat/T2w
cd ${input}

mkdir tmp
# Register planes to same space
for movingImage in `ls ${input}/*T2w*.nii.gz`;
    do
    name=`basename ${movingImage}`
    #movingImage=${file}
    fixedImage=/home/k2252514/templates/nihpd/nihpd_asym_02-05_t2w.nii # Selected based on age of participant
    antsRegistrationSyN.sh -d 3 -f ${fixedImage} -m ${movingImage} -t r	-o ${input}/tmp/reg-${name}
done

# Trasform planes to isotropic image
cd ${input}/tmp
antsMultivariateTemplateConstruction2.sh -d 3 -i 1 -r 1 -k 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t SyN -m MI -c 0 -o isotropic_ reg-site*T2w*.nii.gz



