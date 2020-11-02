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
python "${SolverPath}/tools/DataProcessing/FileExtractor.py" "${DataPath}/" 

echo " "
echo "---------------------------------------"
echo ">>> Normalize images <<<"
echo "---------------------------------------"
python "${SolverPath}/tools/DataProcessing/ImageNormalizer.py" "${DataPath}/" 

echo " "
echo "---------------------------------------"
echo ">>> Remove overlapping voxels in CSF/FLAIR image <<<"
echo "---------------------------------------"
python "${SolverPath}/tools/DataProcessing/VoxelRemover.py" "${DataPath}/" 
