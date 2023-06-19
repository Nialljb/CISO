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
##############################################################################

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

##############################################################################
# Handle INPUT file

# Find input file In input directory with the extension
# .nii, .nii.gz
axi_input_file=`find $INPUT_DIR/axi -iname '*.nii' -o -iname '*.nii.gz'`
cor_input_file=`find $INPUT_DIR/cor -iname '*.nii' -o -iname '*.nii.gz'`
sag_input_file=`find $INPUT_DIR/sag -iname '*.nii' -o -iname '*.nii.gz'`

# Check that input file exists
if [[ -e $axi_input_file ]] && [[ -e $cor_input_file ]] && [[ -e $sag_input_file ]]; then
    echo "${CONTAINER}  Input file found: ${axi_input_file}"
    echo "${CONTAINER}  Input file found: ${cor_input_file}"
    echo "${CONTAINER}  Input file found: ${sag_input_file}"
else
  echo "${CONTAINER} Missing one or more Nifti inputs within input directory $INPUT_DIR"
  exit 1
fi

# Put in one directory (removing the brackets)
cp ${axi_input_file} $work/T2w_AXI.nii.gz
cp ${cor_input_file} $work/T2w_COR.nii.gz 
cp ${sag_input_file} $work/T2w_SAG.nii.gz

##############################################################################
# Run hyperfine-ciso algorithm

# Set initial exit status
hyperfine_ciso_exit_status=0

# Pre-registration
if [ "$(ls -A $work)" ]; then
  for ii in `ls $work`;
      do
      echo "Registering ${ii} to ${target_template}"
      antsRegistrationSyN.sh -d ${imageDimension} -f /flywheel/v0/app/templates/${target_template} -m $work/${ii} -o $work/reg_${ii}
  done
  hyperfine_ciso_exit_status=$?
fi

# Collect output from registration
triplane_input=`ls $work/reg_*nii.gzWarped.nii.gz`
echo ${triplane_input}

# Check for registered files and smush them together
if [[ ! -z $triplane_input ]]; then
    echo "Running antsMultivariateTemplateConstruction2.sh"
    antsMultivariateTemplateConstruction2.sh -d ${imageDimension} -i ${Iteration} -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t ${transformationModel} -m ${similarityMetric} -o ${work}/${prefix} ${triplane_input}
    hyperfine_ciso_exit_status=$?
fi
# Check isotantsMultivariateTemplateConstruction2.sh completed & clean up output
if [[ -e $work/${prefix}template0.nii.gz ]]; then
    echo "Isotropic image generated from othogonal aquisitions"
    echo "Cleaning up..."
    mv $work/${prefix}template0.nii.gz /flywheel/v0/output/${prefix}.nii.gz
    mv $work/reg_*nii.gzWarped.nii.gz /flywheel/v0/output/
    hyperfine_ciso_exit_status=$?
fi

##############################################################################
# Handle Exit status

if [[ $hyperfine_ciso_exit_status == 0 ]]; then
  echo -e "${CONTAINER} Success!"
  exit 0
else
  echo "${CONTAINER}  Something went wrong! hyperfine-ciso exited non-zero!"
  exit 1
fi