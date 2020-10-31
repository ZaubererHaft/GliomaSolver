#!/bin/sh

if [ $LRZ_SYSTEM_SEGMENT != "" ]
then
	source ./setupPython.sh
fi

source ./readInputVariables.sh
python "${SolverPath}/tools/DataProcessing/FileExtractor.py" "${DataPath}/" 
python "${SolverPath}/tools/DataProcessing/ImageNormalizer.py" "${DataPath}/" 