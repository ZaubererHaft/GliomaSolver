#!/bin/bash

#use lib implementation (1=simpleitk, others: nibabel)
LIB=2

if [ $LRZ_SYSTEM_SEGMENT != "" ]
then
	echo "setting up python environment..."
	module load python
	conda create -n py38 python=3.8
	source activate py38
	conda install -c anaconda numpy
	conda install -c simpleitk simpleitk
	conda install scikit-learn
	conda install -c conda-forge nibabel
	echo "done"
fi

. ./readInputVariables.sh

read -p "Need image extraction from seg files and renaming? <y/N> " prompt
echo "option: $prompt"
if [ "y" == "${prompt}" ]
then
	echo " "
	echo "---------------------------------------"
	echo ">>> Extract data from segmentation files <<<"
	echo "---------------------------------------"
	python "${SolverPath}/tools/DataProcessing/FileExtractor.py" "${DataPath}/" $LIB
fi

read -p "Need normalizing FET segementation and clear background intensity? <y/N> " prompt
if [ $prompt == "y" ]
then
	echo " "
	echo "---------------------------------------"
	echo ">>> Normalize images <<<"
	echo "---------------------------------------"
	python "${SolverPath}/tools/DataProcessing/ImageNormalizer.py" "${DataPath}/" $LIB 
fi

echo " "
echo "---------------------------------------"
echo ">>> Remove overlapping voxels in CSF/FLAIR image <<<"
echo "---------------------------------------"
python "${SolverPath}/tools/DataProcessing/VoxelRemover.py" "${DataPath}/" $LIB 

read -p "Need header correction? <y/N> " prompt
if [ $prompt == "y" ]
then
	echo " "
	echo "---------------------------------------"
	echo ">>> Correct nifti header <<<"
	echo "---------------------------------------"
	#ToDo: parametrize correction path
	python "${SolverPath}/tools/DataProcessing/HeaderCorrection.py" "${DataPath}/../../correction/"  "${DataPath}/" $LIB 
fi

