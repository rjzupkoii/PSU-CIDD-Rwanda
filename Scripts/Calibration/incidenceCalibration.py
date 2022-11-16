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

TOLERANCE = 0.1
CALIBRATION_STUDIES = 16




def read_incidence(filename):
  incidence, districts = {}, {}
  with open(filename, 'r') as input:
    # Open the CSV file and skip the header
    reader = csv.reader(input)
    next(reader, None)

    # Create a dictionary with the reference value
    for row in reader:
      incidence[int(row[0])] = float(row[3])
      districts[int(row[0])] = row[2]

  return incidence, districts


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


def check_replicate(replicateId, reference, districts):
  adjustments = []
  cases = 0

  # Iterate over all of the districts in the replicate
  for row in get_incidence(replicateId):
    location = row[1]
    incidence = row[4]
    cases += row[2]
    passing, output = validate(reference[location], incidence, TOLERANCE)
    if not passing:
      adjustments.append(location)
    print("{:11}: {:6} v. {:6} [{}]".format(districts[location], reference[location], incidence, output))

  # Return the total cases and the required adjustments
  return cases, adjustments


def validate(reference, incidence, tolerance):
  PASS = '\033[92m'
  FAIL = '\033[91m'
  CLEAR = '\033[0m'

  passing = ((reference * (1 - tolerance)) < incidence) and \
            (incidence < (reference * (1 + tolerance)))
  if passing:
    return True, PASS + 'PASS' + CLEAR
  return False, FAIL + 'FAIL' + CLEAR


if __name__ == "__main__":
  # Read the reference data
  reference, districts = read_incidence(REFERENCE_INCIDENCE)

  # Process the most recently completed replicate in the calibration study
  replicates = get_replicates(CALIBRATION_STUDIES)
  cases, adjustments = check_replicate(replicates[0][0], reference, districts)

  # Print the remainder of the processing data
  print("Total Clinical: {:,}".format(cases / 0.25))    # PLACEHOLDER adjustment
  print("Acceptable tolerance ±{}".format(TOLERANCE))