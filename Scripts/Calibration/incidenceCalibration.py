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
import ascFile as gis
import database as db

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# Since this script is being written against this repository, we can make some 
# assumptions about the paths.
ADJUSTMENT_FILE = 'data/adjusted_pfpr.asc'
REFERENCE_CONFIGURATION = '../../Studies/rwa-configuration.yml'
REFERENCE_DISTRICTS = '../../GIS/rwa_district.asc'
REFERENCE_INCIDENCE = '../../GIS/rwa_district_incidence_2020.csv'
REFERENCE_PFPR = '../../GIS/rwa_pfpr2to10.asc'

# PLACEHOLDER default values that can be passed via command line
ADJUSTMENT = 0.05
TOLERANCE = 0.1
CALIBRATION_STUDIES = 16


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
          AND md.dayselapsed = 6544
        GROUP BY md.replicateid, msd.location) one
      INNER JOIN (
        SELECT md.replicateid,
          msd.location,
          sum(msd.clinicalepisodes) as clinical
        FROM sim.monthlydata md 
          INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed between 6209 and 6544
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


def adjust_pfpr(pfpr_file, district_file, locations, adjustment):
  # Load the ASC files
  [ascHeader, pfpr] = gis.load_asc(pfpr_file)
  [_, districts] = gis.load_asc(district_file)

  # Process each district indicated
  for district in locations:
    # Find all of the district cells in the PfPR file
    for row in range(0, ascHeader['nrows']):
      for col in range(0, ascHeader['ncols']):
        # If it's a match then apply the adjustment
        if districts[row][col] == district:
          if locations[district] < 0: 
            pfpr[row][col] -= (pfpr[row][col] * adjustment)     # Adjust down
          else:
            pfpr[row][col] += (pfpr[row][col] * adjustment)     # Adjust up
          
  # Write the adjusted file to disk and inform the user
  gis.write_asc(ascHeader, pfpr, ADJUSTMENT_FILE)
  print('Used {} to prepare {} with ±{}% adjustment'.format(pfpr_file, ADJUSTMENT_FILE, adjustment * 100.0))


# Check the replicate indicated to verify that the incidence per 1000 is within
# the indicated tolerance of the reference data.
def check_replicate(replicateId, reference, labels, tolerance):
  adjustments = {}
  cases = 0

  # Iterate over all of the districts in the replicate
  for row in get_incidence(replicateId):
    location = row[1]
    incidence = row[4]
    cases += row[2]

    # Check the incidence in relation to the reference and tolerance
    status, output = validate(reference[location], incidence, tolerance)
    if status != 0:
      adjustments[location] = status
    print("{:11}: {:6} v. {:6} [{}]".format(labels[location], reference[location], incidence, output))

  # Return the total cases and the required adjustments
  return cases, adjustments


# Read the reference incidence data for the districts from the CSV file indicated
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


# Validate that the incidence data provided is within the acceptable tolerance
# of the reference incidence
def validate(reference, incidence, tolerance):
  PASS = '\033[92m'
  FAIL = '\033[91m'
  CLEAR = '\033[0m'

  status = 0
  status -= (reference * (1 + tolerance)) < incidence   # Prevalence needs to be adjusted down
  status += incidence < (reference * (1 - tolerance))   # Prevalence needs to be adjusted up
  if status == 0:
    return status, PASS + 'PASS' + CLEAR
  return status, FAIL + 'FAIL' + CLEAR


def main():
  # Read the reference data
  reference, labels = read_incidence(REFERENCE_INCIDENCE)

  # Process the most recently completed replicate in the calibration study
  replicates = get_replicates(CALIBRATION_STUDIES)
  print("Validating using replicate {}".format(replicates[0][0]))
  cases, adjustments = check_replicate(replicates[0][0], reference, labels, TOLERANCE)

  # Print the remainder of the processing data
  print("Total Clinical: {:,}".format(cases / 0.25))    # PLACEHOLDER adjustment
  print("Acceptable tolerance ±{}%".format(TOLERANCE * 100.0))

  if len(adjustments) != 0:
    pfpr_file = REFERENCE_PFPR
    if os.path.exists(ADJUSTMENT_FILE):
      pfpr_file = ADJUSTMENT_FILE
    adjust_pfpr(pfpr_file, REFERENCE_DISTRICTS, adjustments, ADJUSTMENT)


if __name__ == "__main__":
  # Set up the environment
  if not os.path.exists('data'):
    os.makedirs('data')

  # Run the main script
  main()