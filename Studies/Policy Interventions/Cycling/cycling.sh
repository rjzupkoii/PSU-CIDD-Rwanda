#!/bin/bash

# Script to run the Rwanda drug cycling options.
#
# Note that the calibrationLib.sh from PSU-CIDD-MaSim-Supoort is needed
source ./calibrationLib.sh

# Settings for the cluster
user='rbz5100'
target=130

# Itterate over all of the day combinations
for days  in 90 180 270 365 545 730; do

  # Prepare the job files
  configuration="rwa-cycling-$days.yml"
  sed 's/#DAYS#/'"$days"'/g' rwa-cycling-template.yml > $configuration
  job="rwa-cycling-$days.job"
  sed 's/#FILENAME#/'"$configuration"'/g' rwa-cycling-template.job > $job  

  # Queue the job upto the configured number of times
  count=0
  while [ $count -lt $target ]; do

    # Queue the job
    check_delay $user
    sbatch $job

    # Update the counter
    count=$((count + 1))
    
  done
done