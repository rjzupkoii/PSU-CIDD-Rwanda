#!/bin/bash

# Script to run various 561H spiking combinations.
#
# Note that the calibrationLib.sh from PSU-CIDD-MaSim-Supoort is needed
source ./calibrationLib.sh

# Settings for the cluster
user='rbz5100'
replicates=0

# Iterate over all of the key variables and create the replicates
for year in `seq 2003 1 2013`; do
  for fraction in `seq 0.005 0.005 0.1`; do
    
    # Prepare the files
    configuration="rwa-spike-$year-$fraction.yml"
    sed 's/#YEAR#/'"$year"'/g' rwa-spike-template-10x.yml > $configuration
    sed -i 's/#FRACTION#/'"$fraction"'/g' $configuration
    job="rwa-spike-$year-$fraction.job"
    sed 's/#FILENAME#/'"$configuration"'/g' rwa-spike.job > $job

    # Queue the job
    check_delay $user
    sbatch $job
    let "replicates+=1"
  done
done