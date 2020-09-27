#!/bin/bash

#General Options
#SBATCH -D .                        #Start job in specified directory
#SBATCH --mail-user=     #E-mail Adress (obligatory)
#SBATCH --mail-type=NONE         #change to get email notifications
#SBATCH -J PI                   #Name of batch request (not more than 8 characters or so)
#SBATCH -o jobLog.%j.%N.out      #write standard output to specified file
#SBATCH --export=NONE               #export designated envorinment variables into job script

#Job control
#SBATCH --clusters=cm2_tiny              #cluster to be used (testing: inter)
#SBATCH --partition=cm2_tiny       #cm2_tiny cm2_large      #node on this cluster to be used  (testig: mpp3_inter)
##SBATCH --qos=cm2_std             #cm2_tiny cm2_large      #only required for cm2
#SBATCH --nodes=2                  #number of nodes to be used (each MC2 node has 28 cores btw.)

#Node configuration
##SBATCH --ntasks-per-node=28         #tasks runnable on each node
#SBATCH --tasks=56                #expected amount of tasks
##SBATCH --overcommit               #allow more than one task per CPU
##SBATCH --ntasks-per-core          #tasks per core
#SBATCH --cpus-per-task=1           #specify ampunt of CPUs for every single task

#Other Configuration

#SBATCH --time=01:00:00             #Maximum runtime
#SBATCH --get-user-env

module load slurm_setup

# Modules
source /etc/profile.d/modules.sh
module purge
#module load admin/1.0 lrz/default gsl/2.3 tempdir  #gsl/2.3 causes: "libgsl.so.23 cannot open shared object file no such file or directory"
module load admin lrz tempdir
#WARNING(gsl/2.3): This module is scheduled for retirement.
#WARNING(gcc/4.9): This module is scheduled for retirement.
module load gcc #requirement: tempdir
module load spack

module load intel-parallel-studio   #alternative to "intel" package

module load gsl     #requires intel/19.1.0
#module load matlab   #extracting the Inference output needs this!
module list

echo "Using this mpicc:"
which mpicc

export LANG=C
export LC_ALL=C
export OMP_NUM_THREADS=1    #2 on cm2, 2 on mpp3
#export I_MPI_DEBUG=5       #for additional debug output

echo "In the directory: $PWD"
echo "Running program on $SLURM_NNODES nodes with $SLURM_CPUS_PER_TASK tasks, each with $SLURM_CPUS_PER_TASK cores."
echo "OMP_NUM_THREADS: $OMP_NUM_THREADS"
#echo "SLURM_NTASKS: $SLURM_NTASKS"
#echo "SLURM_NTASKS_PER_NODE: $SLURM_NTASKS_PER_NODE"

mpirun -env TORC_WORKERS 1 ./engine_tmcmc
#mpirun -np 64 -env TORC_WORKERS 1 ./engine_tmcmc

./extractInferenceOutput.sh
