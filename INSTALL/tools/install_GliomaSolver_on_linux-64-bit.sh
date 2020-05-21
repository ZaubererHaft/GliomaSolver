#!/bin/bash

echo "==============================================="
echo "  Installing libraries for the GliomaSolver    "
echo "==============================================="

InstallDir=$(pwd)                       # ".../GliomaSolver/INSTALL"
SolverDir=$(dirname "${InstallDir}")    # ".../GliomaSolver"

echo "Shall this installer also install the libraries for the Bayesian Inference?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) BI="yes"; break;;         #if this variable is set to "yes" the respective libraries for Bayesian Inference will be installed
        No ) BI="no"; break;;
    esac
done


echo "--------------------------------------"
echo ">>> Getting prerequsites and external programms   <<<"
echo "--------------------------------------"



if [ $BI = "yes" ]          # only for Bayesian Inference
then
    sudo apt install gcc gfortran gawk libtool texlive-full pandoc pandoc-citeproc  
    
    #Explaination:    
    #gcc                                    # general prerequsites for building anything
    #gfortran                               # needed for mpich
    #gawk                                   # reliable math calculations with gawk (normal awk is shit)
    #libtool                                # needed for gsl
    #pandoc pandoc-citeproc texlive-full    # converting our results.md into a pdf
else
    sudo apt install gcc gfortran gawk
fi


echo "--------------------------------------"
echo ">>> Downloading externa libraries   <<<"
echo "--------------------------------------"

cd "${SolverDir}"
#wget tdo.sk/~janka/GliomaSolverHome/libs/lib-linux-64-bit/lib.tgz #TODO: update janas package
wget https://syncandshare.lrz.de/getlink/fi6xQsW6vgKxt7DEoQZzjnuS/lib.tgz
tar -zxf lib.tgz
rm lib.tgz

wget tdo.sk/~janka/GliomaSolverHome/libs/lib-linux-64-bit/inference_libs.tgz
tar -zxf inference_libs.tgz
mv inference_libs/* lib/ && rm -r inference_libs
rm inference_libs.tgz


echo " "
echo "--------------------------------------"
echo ">>> Installing libraries   <<<"
echo "--------------------------------------"

cd lib
LIB_BASE=$(pwd)                         # ".../GliomaSolver/lib"

gsl_src=gsl-src
mpich_src=mpich-3.2.1-src
tbb=tbb40_20120613oss
vtk=myVTK
hypre=hypre-2.10.0b


tar -zxf ${mpich_src}.tgz
tar -zxf ${tbb}.tgz
tar -zxf ${vtk}.tgz
tar -zxf ${hypre}.tgz

mkdir -p mpich-install
rm ${tbb}.tgz
rm ${vtk}.tgz
rm ${hypre}.tgz

if [ $BI = "yes" ]          # only for Bayesian Inference 
then
    tar -zxf ${gsl_src}.tgz

    mkdir -p gsl-install
fi


echo "--------------------------------------"
echo " Installing mpich:"
echo "--------------------------------------"

cd "${mpich_src}"
make clean
./configure --prefix="${LIB_BASE}"/mpich-install
make
make install
export PATH="${LIB_BASE}"/mpich-install/bin:$PATH

echo "---------------"
echo "mpicc is set to"
which mpicc
echo "---------------"
cd "${LIB_BASE}"
rm ${mpich_src}.tgz
rm -r ${mpich_src}


echo "--------------------------------------"
echo " Installing tbb:"
echo "--------------------------------------"

cd "${tbb}"
make clean
make
cd "${LIB_BASE}"


echo "--------------------------------------"
echo " Installing Hypre:"
echo "--------------------------------------"
cd "${hypre}/src"
make clean
./configure
make
make install
cd "${LIB_BASE}"

if [ $BI = "yes" ]          # only for Bayesian Inference 
then
    echo "--------------------------------------"
    echo " Installing gsl:"
    echo "--------------------------------------"

    cd "${gsl_src}"
    ./autogen.sh
    ./configure --enable-maintainer-mode --disable-dynamic --prefix="${LIB_BASE}"/gsl-install
    make
    make install
    cd "${LIB_BASE}"
    rm ${gsl_src}.tgz
    #rm -r ${gsl_src}   #gonna throw a "rm: remove write-protected regular file 'gsl-src/gsl-config'?" hindering the flow


    echo "--------------------------------------"
    echo " Installing torc:"
    echo "--------------------------------------"

    cd "${SolverDir}"/tools/pi4u_lite/torc_lite/
    autoreconf
    automake --add-missing
    ./configure CC=mpicc --prefix="${LIB_BASE}"/usr/torc --with-maxnodes=1024
    make
    make install

    export PATH="${LIB_BASE}"/usr/torc/bin:$PATH
    cd "${LIB_BASE}"

    echo "--------------------------------------"
    echo " Compiling Inference tools:"
    echo "--------------------------------------"

    cd "${SolverDir}"/tools/pi4u_lite/Inference

    UserName=$(hostname -s)
    cp tools.make/Makefile .
    cp tools.make/setup_linux.sh setup_${UserName}.sh
    cp tools.make/run_inference.sh .

    sed -i 's|_USER_LIB_BASE_|'"${LIB_BASE}"'|g' Makefile
    sed -i 's|_USER_LIB_BASE_|'"${LIB_BASE}"'|g' setup_${UserName}.sh
    sed -i 's|_USER_LIB_BASE_|'"${LIB_BASE}"'|g' run_inference.sh

    source setup_${UserName}.sh
    make clean
    make

    cd "${LIB_BASE}"
fi


echo " "
echo "--------------------------------------"
echo ">>>       Creating Makefile       <<<"
echo "--------------------------------------"
cd "${SolverDir}"/makefile

UserName=$(hostname -s)
cp tools.make/make.linux make.${UserName}
cp tools.make/Makefile .
cp tools.make/setup_linux.sh setup_${UserName}.sh

#replace placeholders in files
sed -i 's|_USER_LIB_BASE_|'"${LIB_BASE}"'|g' make.${UserName}
sed -i 's|_USER_NAME_|'"${UserName}"'|g' Makefile
sed -i 's|_USER_LIB_BASE_|'"${LIB_BASE}"'|g' setup_${UserName}.sh

source setup_${UserName}.sh

echo "  "
echo "==============================================="
echo ">>>     The Installation is completed       <<<"
echo "==============================================="
echo " "
echo "Please update your .bashrc or similar file to include path to the installed libraries."
echo " To do so, put the text between the following dashed lines into your .bashrc file:"
echo "---------------------------------------"

#cat setup_${UserName}.sh
echo "LIB_BASE=\"${LIB_BASE}\""
echo "export LD_LIBRARY_PATH=\$LIB_BASE/tbb40_20120613oss/build/linux_intel64_gcc_cc4.6.1_libc2.5_kernel2.6.18_release/:\$LD_LIBRARY_PATH"
echo "export LD_LIBRARY_PATH=\$LIB_BASE/myVTK/lib/vtk-5.4/:\$LD_LIBRARY_PATH"
echo "export LD_LIBRARY_PATH=\$LIB_BASE/hypre-2.10.0b/src/hypre/lib/:\$LD_LIBRARY_PATH"
if [ $BI = "yes" ]          # only for Bayesian Inference 
then
    echo "export LD_LIBRARY_PATH=\$LIB_BASE/gsl-install/lib/:\$LD_LIBRARY_PATH"
    echo "export PATH=\$LIB_BASE/usr/torc/bin:\$PATH"
    #cat "${SolverDir}/tools/pi4u_lite/Inference/setup_${UserName}.sh"
fi
echo "export PATH=\$LIB_BASE/mpich-install/bin:\$PATH"

echo "---------------------------------------"
echo "To compile the GliomaSolver do"
echo "make clean && make -j 4"
echo "==============================================="

