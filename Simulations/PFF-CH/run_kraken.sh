# Threads:
N=8
export OMP_NUM_THREADS=$N

# Path to patient data
DATA_BASE=/home/jana/Work/GliomaAdvance/GliomaSolver/Anatomy
PatFileName=$DATA_BASE/Patient00/P00

# brain simulation set up
program=brain
model=PFFCH
verbose=1
adaptive=1
vtk=1
dumpfreq=25
bDumpIC=1
Niter=300
width=12

echo "In the directory: $PWD"
echo "Running program on $N nodes."

./$program -nthreads $N -model $model -verbose $verbose -adaptive $adaptive -PatFileName $PatFileName -vtk $vtk -dumpfreq $dumpfreq -bDumpIC $bDumpIC -Niter $Niter -widt $widt 
