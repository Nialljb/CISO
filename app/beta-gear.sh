#!/bin/bash
# https://wiki.mouseimaging.ca/display/MICePub/Image+registration+and+ANTs+tools

source $FSLDIR/etc/fslconf/fsl.sh

# inputs
axi=`jq -r '.inputs.axi.location.path' /flywheel/v0/config.json`; cp ${axi} /flywheel/v0/work/T2w_AXI.nii.gz
cor=`jq -r '.inputs.cor.location.path' /flywheel/v0/config.json`; cp ${cor} /flywheel/v0/work/T2w_COR.nii.gz 
sag=`jq -r '.inputs.sag.location.path' /flywheel/v0/config.json`; cp ${sag} /flywheel/v0/work/T2w_SAG.nii.gz

# app options
imageDimension=`jq -r '.config.imageDimension ' /flywheel/v0/config.json`
Iteration=`jq -r '.config.Iteration ' /flywheel/v0/config.json`
transformationModel=`jq -r '.config.transformationModel ' /flywheel/v0/config.json`
similarityMetric=`jq -r '.config.similarityMetric ' /flywheel/v0/config.json`
target_template=`jq -r '.config.target_template ' /flywheel/v0/config.json`
prefix=`jq -r '.config.prefix ' /flywheel/v0/config.json`

for ii in `ls /flywheel/v0/work/`;
    do
    echo "ii is ${ii}"
    antsRegistrationSyN.sh -d ${imageDimension} -f /flywheel/v0/app/templates/${target_template} -m /flywheel/v0/work/${ii} -t r -o /flywheel/v0/work/reg_${ii}
done

antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o /flywheel/v0/work/${prefix} /flywheel/v0/work/reg_*.nii.gz
mv /flywheel/v0/work/${prefix}template0.nii.gz /flywheel/v0/output/${prefix}.nii.gz
mv /flywheel/v0/work/reg* /flywheel/v0/output/
