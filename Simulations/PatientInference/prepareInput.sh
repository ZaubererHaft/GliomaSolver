#!/bin/sh

if [ $LRZ_SYSTEM_SEGMENT != "" ]
then
    ./setupPython.sh
fi

InputFile=Input.txt
DataPath=$(  cat ${InputFile} | awk -F '=' '/^DataPath/ {print $2}')
SolverPath=$(cat ${InputFile} | awk -F '=' '/^SolverPath/ {print $2}')

#remove terminating "/" if existing
SolverPath=$(dirname $SolverPath)"/"$(basename $SolverPath)				
DataPath=$(dirname $DataPath)"/"$(basename $DataPath)	 

python3 "${SolverPath}/tools/DataProcessing/FileExtractor.py" "${DataPath}/" 