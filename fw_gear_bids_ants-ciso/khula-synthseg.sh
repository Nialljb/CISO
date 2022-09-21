#!/bin/bash 

echo "hello from khula-SR.sh"

wd=/data/project/Khula_LEAP/sandbox/Khula/source
der=/data/project/Khula_LEAP/sandbox/Khula/derivatives
for sub in `ls ${wd}`; 
    do
    for ses in `ls ${wd}/${sub}`
        do
        # vars
        # t1=`ls ${wd}/${sub}/${ses}/anat/T2w/site*T1w_axi.nii.gz`
        t2=`ls ${der}/${sub}/${ses}/anat/T2w/site*_T2w_axicorsag.nii `
        synth=${wd}/${sub}/${ses}/anat/synthSeg
        mkdir -p ${synth}

        # run command
        echo "running ${sub}"
        mri_synthseg --i ${t2} --o ${synth} --parc --robust --vol ${synth}/VOL --qc ${synth}/QC --threads 8 --cpu

    done
done

# usage: mri_synthseg [--i I] [--o O] [--parc] [--robust] [--fast] [--vol VOL] [--qc QC] [--post POST] [--resample RESAMPLE] [--crop CROP [CROP ...]] [--threads THREADS] [--cpu] [--v1]

# SynthSeg

# optional arguments:
#   -h, --help            show this help message and exit
#   --i I                 Image(s) to segment. Can be a path to an image or to a folder.
#   --o O                 Segmentation output(s). Must be a folder if --i designates a folder.
#   --parc                (optional) Whether to perform cortex parcellation.
#   --robust              (optional) Whether to use robust predictions (slower).
#   --fast                (optional) Bypass some processing for faster prediction.
#   --vol VOL             (optional) Output CSV file with volumes for all structures and subjects.
#   --qc QC               (optional) Output CSV file with qc scores for all subjects.
#   --post POST           (optional) Posteriors output(s). Must be a folder if --i designates a folder.
#   --resample RESAMPLE   (optional) Resampled image(s). Must be a folder if --i is a folder.
#   --crop CROP [CROP ...]
#                         (optional) Only analyse an image patch of the given size.
#   --threads THREADS     (optional) Number of cores to be used. Default is 1.
#   --cpu                 (optional) Enforce running with CPU rather than GPU.
#   --v1                  (optional) Use SynthSeg 1.0 (updated 25/06/22).