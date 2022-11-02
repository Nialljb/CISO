#!/bin/bash

# Job wrapper
logs=/home/k2252514/sgeLogs
echo -n "" > ${logs}/regJob.txt
job=${logs}/regJob.txt

# set job
source=/data/project/Khula_LEAP/sandbox/Khula/data/source

for sub in `ls ${source}`;
    do
    for sesh in `ls ${source}/${sub}/`;
        do
        ses=`basename ${sesh}`
        #echo ${ses}
        echo "module load ants; ${HOME}/repos/beta/combinePlanes.sh ${source} ${sub} ${ses}" >> ${job}
    done
done

# Run job
${HOME}/repos/nanTools/hpcSubmit_SGE ${job} 06:00:00 3 10G
echo ""; echo "***"; echo ""; echo "Submitted commands:"; head ${job}