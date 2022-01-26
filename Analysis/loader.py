#!/usr/bin/python3

# loader.py
# 
# Load the relevent data for the study from the database.
import csv
import os
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from database import select
from utility import progressBar


# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# Path for the replicate data and data sets
REPLICATE_DIRECTORY = 'data/replicates'
DATASET_DIRECTORY = 'data/datasets'

# Path for the replicates list
REPLICATES_LIST = 'data/rwa-replicates.csv'

# The number of replicates to pull to the size as our data set
REPLICATE_COUNT = 50


def get_replicates():
  sql = """
      SELECT c.id AS configurationid, 
        c.studyid, 
        c.filename, 
        r.id AS replicateid, 
        r.starttime, 
        r.endtime
      FROM sim.replicate r
        INNER JOIN sim.configuration c ON c.id = r.configurationid
      WHERE r.endtime IS NOT null
        AND c.studyid > 2
      ORDER BY c.studyid, c.filename, r.id"""
  return select(CONNECTION, sql, None)


def get_replicate(replicateId):
  sql = """
      SELECT c.id as configurationid, sd.replicateid, sd.dayselapsed,
        sd.district, infectedindividuals,  clinicalepisodes, 
        CASE WHEN gd.occurrences IS NULL THEN 0 else gd.occurrences END AS occurrences,
        CASE WHEN gd.clinicaloccurrences IS NULL THEN 0 else gd.clinicaloccurrences END AS clinicaloccurrences,
        CASE WHEN gd.weightedoccurrences IS NULL THEN 0 else gd.weightedoccurrences END AS weightedoccurrences,
        treatmentfailures,
        genotypecarriers
      FROM (
        SELECT md.replicateid, md.dayselapsed, msd.location AS district,
          sum(msd.infectedindividuals) AS infectedindividuals, 
          sum(msd.clinicalepisodes) AS clinicalepisodes,
          sum(msd.treatmentfailures) as treatmentfailures,
          sum(genotypecarriers) as genotypecarriers
        FROM sim.monthlydata md
          INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed > (11 * 365)
        GROUP BY md.replicateid, md.dayselapsed, msd.location) sd
      LEFT JOIN (
        SELECT md.replicateid, md.dayselapsed, mgd.location AS district,
        sum(mgd.occurrences) AS occurrences,
          sum(mgd.clinicaloccurrences) AS clinicaloccurrences,
          sum(mgd.weightedoccurrences) AS weightedoccurrences
        FROM sim.monthlydata md
          INNER JOIN sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
          INNER JOIN sim.genotype g on g.id = mgd.genomeid
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed > (11 * 365)
          AND g.name ~ '^.....H.'
        GROUP BY md.replicateid, md.dayselapsed, mgd.location) gd ON (gd.replicateid = sd.replicateid 
          AND gd.dayselapsed = sd.dayselapsed
          AND gd.district = sd.district)
        INNER JOIN sim.replicate r on r.id = sd.replicateid
        INNER JOIN sim.configuration c on c.id = r.configurationid
      WHERE r.endtime is not null
        AND r.id = %(replicateId)s
      ORDER BY replicateid, dayselapsed"""
  return select(CONNECTION, sql, {'replicateId':replicateId})  


def merge_data(replicates, outfile):
  # Read the first file so we have something to append to
  infile = os.path.join(REPLICATE_DIRECTORY, "{}.csv".format(replicates[0]))
  data = pd.read_csv(infile, header=None)

  for replicate in replicates[1:]:
    infile = os.path.join(REPLICATE_DIRECTORY, "{}.csv".format(replicate))
    working = pd.read_csv(infile, header=None)
    data = data.append(working)

  data.to_csv(outfile, header=None, index=False)
    

def process_datasets():
  print("Preparing data sets...")
  replicates = pd.read_csv(REPLICATES_LIST, header=None)
  configurations = replicates[2].unique()

  count = 0
  progressBar(count, len(configurations))
  for configuration in configurations:
    data = replicates[replicates[2] == configuration]
    filename = os.path.join(DATASET_DIRECTORY, configuration.replace('yml', 'csv'))
    merge_data(data[-50:][3].to_numpy(), filename)
    count = count + 1
    progressBar(count, len(configurations))


def process_replicates():
# Process the replicates to make sure we have all of the data we need locally

  print("Querying for replicates list...")
  replicates = get_replicates()
  save_csv(REPLICATES_LIST, replicates)
  
  print("Processing replicates...")  
  count = 0
  progressBar(count, len(replicates))
  for row in replicates:
    # Check to see if we already have the data
    filename = os.path.join(REPLICATE_DIRECTORY, "{}.csv".format(row[3]))
    if os.path.exists(filename): continue

    # Query and store the data
    replicate = get_replicate(row[3])
    save_csv(filename, replicate)

    # Update the progress bar
    count = count + 1
    progressBar(count, len(replicates))

  if count != len(replicates): progressBar(len(replicates), len(replicates))


def save_csv(filename, data):
  with open(filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in data:
      writer.writerow(row)


def main():
  if not os.path.exists(REPLICATE_DIRECTORY): os.makedirs(REPLICATE_DIRECTORY)
  if not os.path.exists(DATASET_DIRECTORY): os.makedirs(DATASET_DIRECTORY)

  # Download all of the replicate data locally, then we need to pull the 
  # relevent replicates to the side as the data set for plotting. Since the 
  # project is iterating quickly this will save on needing to clean-up the 
  # database.
  process_replicates()
  process_datasets()


if __name__ == '__main__':
  main()