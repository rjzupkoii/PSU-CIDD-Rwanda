#!/usr/bin/python3

# incidenceCalibration.py
#
# Calibrate the beta values for Rwanda based upon the district incidence rate 
# as opposed to the cell-specific PfPR values.
import os
import sys

# Import our libraries / re-usable code
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python')
from createBetaMap import create_beta_map

# Since this script is being written against this repository, we can make some 
# assumptions about the paths.
REFERENCE_CONFIGURATION = '../../Studies/rwa-configuration.yml'
REFERENCE_PFPR = '../../GIS/rwa_pfpr2to10.asc'

# Query to retrieve the possible mappings and bins
SELECT_MAPPINGS = r"""
SELECT one.replicateid,
  one.location,
  two.clinical,
  one.population,
  round(two.clinical / (one.population / 1000.0), 2) as clinical_per
FROM (
  SELECT md.replicateid,
    msd.location,
     sum(msd.population) as population
  FROM sim.monthlydata md 
    INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
  WHERE md.replicateid = %(replicateId)s
    AND md.dayselapsed = 4352
  GROUP BY md.replicateid, msd.location) one
INNER JOIN (
  SELECT md.replicateid,
    msd.location,
    sum(msd.clinicalepisodes) as clinical
  FROM sim.monthlydata md 
    INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
  WHERE md.replicateid = %(replicateId)s
    AND md.dayselapsed BETWEEN 4015 AND 4380
  GROUP BY md.replicateid, msd.location) two 
ON one.replicateid = two.replicateid AND one.location = two.location
ORDER BY one.location
"""

if __name__ == "__main__":
    print("test")