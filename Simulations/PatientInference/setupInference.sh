#!/bin/sh

echo "------------------------------------------------------"
echo "          SETTING-UP INFERENCE ENVIROMENT             "
echo "------------------------------------------------------"

if [ $LRZ_SYSTEM_SEGMENT != "" ]
then
    module load matlab
    source ./setupPython.sh
fi

#reads the input variables used within this script
source ./readInputVariables.sh

#remove overlap before conversion to dat
echo " "
echo "---------------------------------------"
echo ">>> Remove overlapping voxels in CSF/FLAIR image <<<"
echo "---------------------------------------"
python "${SolverPath}/tools/DataProcessing/VoxelRemover.py" "${DataPath}/Tum_FLAIR.nii.gz" "${DataPath}/CSF.nii.gz"

echo " "
echo "---------------------------------------"
echo ">>> Converting Input data nii2dat <<<"
echo "---------------------------------------"
MatlabTools="${SolverPath}/tools/DataProcessing/source"
MyBase=$(pwd)
cd "${MatlabTools}"
bRotate=1
bResize=1
matlab -nodisplay -nojvm -nosplash -nodesktop -r "nii2dat('${DataPath}/',${bRotate},${bResize}); exit"
cd "$MyBase"

MRAGInputData=${DataPath}_dat/

# Folders name
PrepFolder=Preprocessing
TMP=Inference/TMPTMP/
LIKELIHOOD=Inference/Likelihood/makefile/


# Get Inference tools and scripts
cp -r "$SolverPath/tools/pi4u_lite/Inference" .
cp -r "$SolverPath/tools/scripts" . 


echo " "
echo "---------------------------------------"
echo ">>> Data Preprocessing <<<"
echo "---------------------------------------"
# Map data to MRAG grid
mkdir -p $PrepFolder
cp brain $PrepFolder
cp scripts/mapDataToMRAGrid.sh $PrepFolder
cp scripts/writeRunAll.sh $PrepFolder/
cp scripts/writeTMCMCpar.sh $PrepFolder/
cp scripts/GenericPrior.txt $PrepFolder/


cd $PrepFolder
./mapDataToMRAGrid.sh "$MRAGInputData" > PreprocessingReport.txt
echo " "
echo "---------------------------------------"
echo ">>> Setting up Patient-Specific Enviroment <<<"
echo "---------------------------------------"
./writeRunAll.sh "$MRAGInputData"
./writeTMCMCpar.sh $Nsamples

# Copy where they belong
cp brain ../$TMP
cp *dat ../$TMP
cp runAll.sh ../$TMP
cp tmcmc_glioma.par ../Inference/ 
cp ../${InputFile} ../Inference/

# Likelihood
cd ../${LIKELIHOOD}
make clean && make
cp likelihood ../../TMPTMP


echo " "
echo " "
echo "------------------------------------------------------"
echo "              DONE WITH THE SET-UP                    "
echo "------------------------------------------------------"
echo "To run the inference, please go to folder Inference/ and use run_inference.sh or run_inference_lrz.sh script (depending on your enviroment)."
echo "..........................................................."
echo "NOTE: Consider using tmux or cluster job handling system to run the inference."
echo "..........................................................."
