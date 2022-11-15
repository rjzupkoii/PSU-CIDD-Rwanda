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
SELECT replicateid,
    cast(fileparts[1] as numeric) as zone,
    cast(fileparts[2] as numeric) as population,
    cast(fileparts[3] as numeric) as access,
    cast(fileparts[4] as numeric) as beta,
    eir,
    pfpr2to10,
    round(clinical / (population / 1000.0), 2) as incidence
FROM (
    SELECT replicateid,
        regexp_matches(filename, '^([\d\.]*)-(\d*)-([\.\d]*)-([\.\d]*)') as fileparts,
        avg(eir) AS eir, 
        avg(pfpr2to10) AS pfpr2to10,
        max(clinicalepisodes) as clinical,
        max(msd.population) as population
    FROM sim.configuration c
        INNER JOIN sim.replicate r on r.configurationid = c.id
        INNER JOIN sim.monthlydata md on md.replicateid = r.id
        INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
    WHERE c.studyid = %(studyId)s
        AND md.dayselapsed BETWEEN 4015 AND 4380
    GROUP BY replicateid, filename) iq
ORDER BY zone, population, access, pfpr2to10
"""

if __name__ == "__main__":
    print("test")