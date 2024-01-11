#!/bin/bash
# 
# Run script for flywheel/ciso Gear.
#
# Authorship: Niall bourke
#
# https://wiki.mouseimaging.ca/display/MICePub/Image+registration+and+ANTs+tools
##############################################################################

# Define directory names and containers
source $FSLDIR/etc/fslconf/fsl.sh
FLYWHEEL_BASE=/flywheel/v0
INPUT_DIR=$FLYWHEEL_BASE/input
CONTAINER='[flywheel/hyperfine-ciso]'
work=/flywheel/v0/work
mkdir -p ${work}

pixdim=${1}
echo "ciso-gear: pixdim = $pixdim"

##############################################################################

# Check for required files
# Parse configuration
function parse_config {

  CONFIG_FILE=$FLYWHEEL_BASE/config.json
  MANIFEST_FILE=$FLYWHEEL_BASE/manifest.json

  if [[ -f $CONFIG_FILE ]]; then
    echo "$(cat $CONFIG_FILE | jq -r '.config.'$1)"
  else
    CONFIG_FILE=$MANIFEST_FILE
    echo "$(cat $MANIFEST_FILE | jq -r '.config.'$1'.default')"
  fi
}
 
# define app options
imageDimension="$(parse_config 'imageDimension')" # `jq -r '.config.imageDimension ' /flywheel/v0/config.json`
Iteration="$(parse_config 'Iteration')" #`jq -r '.config.Iteration ' /flywheel/v0/config.json`
transformationModel="$(parse_config 'transformationModel')"   # `jq -r '.config.transformationModel ' /flywheel/v0/config.json`
similarityMetric="$(parse_config 'similarityMetric')"   #`jq -r '.config.similarityMetric ' /flywheel/v0/config.json`
target_template="$(parse_config 'target_template')"    #`jq -r '.config.target_template ' /flywheel/v0/config.json`
prefix="$(parse_config 'prefix')" #`jq -r '.config.prefix ' /flywheel/v0/config.json`
phantom="$(parse_config 'phantom')" #`jq -r '.config.prefix ' /flywheel/v0/config.json`

##############################################################################
# Handle INPUT file

# Find input file In input directory with the extension
# .nii, .nii.gz
axi_input_file=`find $INPUT_DIR/axi -iname '*.nii' -o -iname '*.nii.gz'`
cor_input_file=`find $INPUT_DIR/cor -iname '*.nii' -o -iname '*.nii.gz'`
sag_input_file=`find $INPUT_DIR/sag -iname '*.nii' -o -iname '*.nii.gz'`

if [[ "$axi_input_file" == *"Fast"* ]]; then
    echo "Fast detected in axi_input_file"
    prefix=${prefix}_fast
    echo "prefix is now: $prefix"
fi

# Check that input file exists
if [[ -e $axi_input_file ]] && [[ -e $cor_input_file ]] && [[ -e $sag_input_file ]]; then
    echo "${CONTAINER}  Input file found: ${axi_input_file}"
    cp ${axi_input_file} ${work}/T2w_AXI.nii.gz
    echo "${CONTAINER}  Input file found: ${cor_input_file}"
    cp ${cor_input_file} ${work}/T2w_COR.nii.gz 
    echo "${CONTAINER}  Input file found: ${sag_input_file}"
    cp ${sag_input_file} ${work}/T2w_SAG.nii.gz
else
  echo "** ${CONTAINER} Missing one or more Nifti inputs within input directory $INPUT_DIR **"
  prefix=${prefix}-AXI
  if [[ -e $cor_input_file ]]; then
    echo "${CONTAINER}  Input file found: ${cor_input_file}"
    cp ${cor_input_file} ${work}/T2w_COR.nii.gz
    prefix=${prefix}-COR
  else
    echo "${CONTAINER}  Missing coronal input file"
  fi
  if [[ -e $sag_input_file ]]; then
    echo "${CONTAINER}  Input file found: ${sag_input_file}"
    cp ${sag_input_file} ${work}/T2w_SAG.nii.gz
    prefix=${prefix}-SAG
  else
    echo "${CONTAINER}  Missing sagittal input file"
  fi

  # echo "${CONTAINER} Exiting..."
  # exit 1
fi

echo "work directory contents:"
echo "$(ls -l $work)"
##############################################################################
# Run hyperfine-ciso algorithm
echo "${CONTAINER}  Running hyperfine-ciso algorithm"

if [[ $phantom == "true" ]]; then
    echo "Ahhh Phantom data detected, running ghost protocol.."

    # Create a isotropic image from the 3 T2 images
    echo "Running antsMultivariateTemplateConstruction2.sh with rigid registration to axial image..."
    antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -z ${work}/T2w_AXI.nii.gz -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/tmp_${prefix} ${work}/T2w_AXI.nii.gz ${work}/T2w_COR.nii.gz ${work}/T2w_SAG.nii.gz
    echo "Resampling intermediate template to isotropic 1.5mm..."
    ResampleImageBySpacing 3 ${work}/tmp_${prefix} ${work}/resampledTemplate.nii.gz 1.5 1.5 1.5
    echo "Running antsMultivariateTemplateConstruction2.sh with non-linear registration to resampled template..."
    antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -z ${work}/resampledTemplate.nii.gz -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/${prefix} ${work}/T2w_AXI.nii.gz ${work}/T2w_COR.nii.gz ${work}/T2w_SAG.nii.gz
    echo "Cleaning up..."
    mv $work/${prefix}template0.nii.gz /flywheel/v0/output/phantom_${prefix}.nii.gz
    exit 0

else

  echo "Processing in-vivo data..."
  if [[ $target_template == "None" ]]; then
    echo "***"
    echo "No target template specified, trying self-reference..."
    echo "WARNING: BETA FEATURE - May not work as expected..."
    echo "Check output for quality control!"
    echo "***"
    
    # Create a template from the 3 T2 images
    echo "Running antsMultivariateTemplateConstruction2.sh with rigid registration to axial image..."
    antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -z ${work}/T2w_AXI.nii.gz -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/tmp_${prefix} ${work}/* #T2w_AXI.nii.gz ${work}/T2w_COR.nii.gz ${work}/T2w_SAG.nii.gz
    echo "Resampling intermediate template to isotropic 1.5mm..."
    ResampleImageBySpacing 3 ${work}/tmp_${prefix} ${work}/resampledTemplate.nii.gz 1.5 1.5 1.5
    echo "Running antsMultivariateTemplateConstruction2.sh with non-linear registration to resampled template..."
    antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -z ${work}/resampledTemplate.nii.gz -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/${prefix} ${work}/* #T2w_AXI.nii.gz ${work}/T2w_COR.nii.gz ${work}/T2w_SAG.nii.gz
    echo "Cleaning up..."
    mv $work/${prefix}template0.nii.gz /flywheel/v0/output/${prefix}.nii.gz
    exit 0
  
    else
  
    echo "Target template specified: ${target_template}"
    echo "Resampling template to match input resolution 1.5mm"
    # Resample high resolution template to match input (1.5mm)
    ResampleImageBySpacing 3 /flywheel/v0/app/templates/${target_template} /flywheel/v0/app/templates/resampled_${target_template} 1.5 1.5 1.5

    # Pre-registration
    if [ "$(ls -A $work)" ]; then
      for ii in `ls $work`;
          do
          echo "Registering ${ii} to ${target_template}"
          outname=`basename ${ii} .nii.gz`
          # echo "outname is: $outname"
          antsRegistrationSyN.sh -d ${imageDimension} -f /flywheel/v0/app/templates/resampled_${target_template} -m $work/${ii} -o $work/reg_${outname}_
      done
    else
      echo "${CONTAINER}  Pre-registration: No files found in $work"
      echo "${CONTAINER}  Exiting..."
      exit 1
    fi

    # Collect output from registration
    triplane_input=`ls $work/reg_*_Warped.nii.gz`
    echo "Files for reconstruction: "
    echo ${triplane_input}

    # Check for registered files and smush them together
    if [[ ! -z $triplane_input ]]; then
        echo "Running antsMultivariateTemplateConstruction2.sh"
        antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/${prefix} ${triplane_input}
    fi

    # Check isotantsMultivariateTemplateConstruction2.sh completed & clean up output
    if [[ -e $work/${prefix}template0.nii.gz ]]; then
        echo "Isotropic image generated from othogonal aquisitions"
        echo "Cleaning up..."
        mv $work/${prefix}template0.nii.gz /flywheel/v0/output/${prefix}.nii.gz
        mv $work/reg_*_Warped.nii.gz /flywheel/v0/output/
    else
        echo "${CONTAINER} Template not generated!"
        echo "Work directory contents:"
        ls -l $work
        echo "${CONTAINER} Exiting..."
        exit 1
    fi
  fi
fi
