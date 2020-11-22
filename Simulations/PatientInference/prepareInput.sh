#!/bin/sh

if [ $LRZ_SYSTEM_SEGMENT != "" ]
then
	source ./setupPython.sh
fi

source ./readInputVariables.sh

echo " "
echo "---------------------------------------"
echo ">>> Extract data from segmentation files <<<"
echo "---------------------------------------"
python "${SolverPath}/tools/DataProcessing/FixIt.py" "${DataPath}/brats_fla.nii.gz" "${DataPath}/"  
