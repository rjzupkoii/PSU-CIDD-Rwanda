#!/bin/bash

./incidenceCalibration.py
cd ../../Studies
../../PSU-CIDD-MaSim-Support/Python/createBetaMap.py -c rwa-configuration.yml -g ../GIS/ --cache --pfpr ../Scripts/Calibration/data/adjusted_pfpr.asc
cp -r out/ ../Scripts/Calibration/