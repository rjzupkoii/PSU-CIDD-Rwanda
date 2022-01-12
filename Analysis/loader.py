#!/usr/bin/python3

# loader.py
# 
# Load the relevent data for the study from the database.
import csv
import os
import sys

sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from database import select
from utility import progressBar


# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# Path for the replicate data
DATA_DIRECTORY = 'data/replicates'

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
        CASE WHEN gd.weightedoccurrences IS NULL THEN 0 else gd.weightedoccurrences END AS weightedoccurrences
      FROM (
        SELECT md.replicateid, md.dayselapsed, msd.location AS district,
          sum(msd.infectedindividuals) AS infectedindividuals, 
          sum(msd.clinicalepisodes) AS clinicalepisodes
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
    filename = os.path.join(DATA_DIRECTORY, "{}.csv".format(row[3]))
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
  if not os.path.exists(DATA_DIRECTORY): os.makedirs(DATA_DIRECTORY)

  process_replicates()

  # Now that we have all of the replicate data locally, we need to pull the 
  # relevent replicates to the side as the data set for plotting. Since the 
  # project is iterating quickly this will save on needing to clean-up the 
  # database.



if __name__ == '__main__':
  main()