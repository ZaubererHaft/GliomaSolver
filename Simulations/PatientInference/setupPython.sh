#!/bin/sh

echo "setting up python environment..."
module load python
conda create -n py38 python=3.8
source activate py38
conda install -c anaconda numpy
conda install -c simpleitk simpleitk
echo "done"