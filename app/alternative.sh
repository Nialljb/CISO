# Isotropic T2 template creation without pre-registration to a target template
# Creates an intermediate reference template from the 3 T2 input images

# Create a template from the 3 T2 images
# start with a rigid registration to the first imagem (axial)
antsMultivariateTemplateConstruction2.sh -d 3 -i 4 -z 5_T2_AXI.nii.gz -r 1 -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t SyN -m MI -o ../output/iso1_ 5_T2_AXI.nii.gz 6_T2_Weighted_FSE_SAG.nii.gz 7_T2_Weighted_FSE_COR.nii.gz
# Resample intermediate template to isotropic 1.5mm
ResampleImageBySpacing 3 ../output/iso1_template0.nii.gz ../output/resampledTemplate.nii.gz 1.5 1.5 1.5
# Final template
# Non-linear registration to the resampled template
antsMultivariateTemplateConstruction2.sh -d 3 -i 4 -z ../output/resampledTemplate.nii.gz -f 4x2x1 -s 2x1x0vox -q 30x20x4 -t SyN -m MI -o ../output/iso2_ 5_T2_AXI.nii.gz 6_T2_Weighted_FSE_SAG.nii.gz 7_T2_Weighted_FSE_COR.nii.gz