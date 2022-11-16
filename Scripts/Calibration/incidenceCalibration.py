#!/usr/bin/python3

# incidenceCalibration.py
#
# Calibrate the beta values for Rwanda based upon the district incidence rate 
# as opposed to the cell-specific PfPR values.
import csv
import os
import sys

# Import our libraries / re-usable code
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import database as db

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# Since this script is being written against this repository, we can make some 
# assumptions about the paths.
REFERENCE_CONFIGURATION = '../../Studies/rwa-configuration.yml'
REFERENCE_PFPR = '../../GIS/rwa_pfpr2to10.asc'
REFERENCE_INCIDENCE = '../../GIS/rwa_district_incidence_2020.csv'

CALIBRATION_STUDIES = 16


def read_incidence(filename):
  results = {}
  with open(REFERENCE_INCIDENCE, 'r') as input:
    # Open the CSV file and skip the header
    reader = csv.reader(input)
    next(reader, None)

    # Create a dictionary with the reference value
    for row in reader:
      results[row[0]] = row[3]

  return results


def get_incidence(replicateId):
  sql = """
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
  return db.select(CONNECTION, sql, {'replicateId': replicateId})


def get_replicates(studyId):
  sql = """
      SELECT r.id
      FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
      WHERE c.studyid = %(studyId)s
        AND r.endtime IS NOT NULL
      ORDER BY r.endtime DESC
      """
  return db.select(CONNECTION, sql, {'studyId': studyId})


if __name__ == "__main__":
  incidence = read_incidence(REFERENCE_INCIDENCE)

  replicates = get_replicates(CALIBRATION_STUDIES)
  replicateId = replicates[0][0]

  results = get_incidence(replicateId)
  print(results)