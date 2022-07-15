#!/usr/bin/python3

# loader.py
# 
# Load the relevent data for the study from the database.
import csv
import datetime
import os
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from database import select
from utility import progressBar

# From the Plotting directory
sys.path.insert(1, '../Ploting')
import rwanda

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# Path for the locally cached / processed data
DATASET_DIRECTORY = 'data/datasets'
REPLICATE_DIRECTORY = 'data/replicates'
SPIKE_DIRECTORY = 'data/spikes'

# Path for the replicates list
REPLICATES_LIST = 'data/rwa-replicates.csv'

# The number of replicates to pull to the size as our data set
REPLICATE_COUNT = 100

# Flag to indicate if we are doing a manuscript run or not
MANUSCRIPT = True

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
      WHERE r.endtime IS NOT null AND c.id in (
        SELECT max(c.id)
        FROM sim.configuration c
        WHERE c.filename in (
          SELECT distinct c.filename
          FROM sim.configuration c
          WHERE c.studyid NOT IN (1, 2, 3, 10))
        GROUP BY c.filename, c.studyid)
      ORDER BY c.studyid, c.filename, r.id"""
  return select(CONNECTION, sql, None)


def get_replicate(replicateId):
  sql = """
      SELECT c.id as configurationid, sd.replicateid, sd.dayselapsed,
        sd.district, infectedindividuals,  clinicalepisodes, 
        CASE WHEN gd.occurrences IS NULL THEN 0 else gd.occurrences END AS occurrences,
        CASE WHEN gd.clinicaloccurrences IS NULL THEN 0 else gd.clinicaloccurrences END AS clinicaloccurrences,
        CASE WHEN gd.weightedoccurrences IS NULL THEN 0 else gd.weightedoccurrences END AS weightedoccurrences,
        treatments,
        treatmentfailures,
        genotypecarriers
      FROM (
        SELECT md.replicateid, md.dayselapsed, msd.location AS district,
          sum(msd.infectedindividuals) AS infectedindividuals, 
          sum(msd.clinicalepisodes) AS clinicalepisodes,
          sum(msd.treatments) AS treatments,
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


def get_genotype_replicate(replicateId):
  sql = """
      SELECT monthly.replicateid, monthly.dayselapsed,
        population, infectedindividuals, clinicalepisodes, treatments, treatmentfailures, pfpr2to10,
        occurances_561h, clinical_561h, weighted_561h, 
        occurances_plasmepsin2x, clinical_plasmepsin2x, weighted_plasmepsin2x,
        occurances_double, clinical_double, weighted_double
      FROM (       
        SELECT md.replicateid, md.dayselapsed,
          sum(msd.population) as population,
          sum(msd.infectedindividuals) AS infectedindividuals, 
          sum(msd.clinicalepisodes) AS clinicalepisodes,
          sum(msd.treatments) AS treatments,
          sum(msd.treatmentfailures) as treatmentfailures,
          round(cast(sum(msd.population * msd.pfpr2to10) / sum(msd.population) as decimal), 3) as pfpr2to10
        FROM sim.monthlydata md
          INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed > (11 * 365)
        GROUP BY md.replicateid, md.dayselapsed) as monthly INNER JOIN (
        SELECT md.replicateid, md.dayselapsed,
          sum(case when g.name ~ '^.....H.' then mgd.occurrences else 0 end) as occurances_561h,
          sum(case when g.name ~ '^.....H.' then mgd.clinicaloccurrences else 0 end) as clinical_561h,
          sum(case when g.name ~ '^.....H.' then mgd.weightedoccurrences else 0 end) as weighted_561h,
          sum(case when g.name ~ '^......2' then mgd.occurrences else 0 end) as occurances_plasmepsin2x,
          sum(case when g.name ~ '^......2' then mgd.clinicaloccurrences else 0 end) as clinical_plasmepsin2x,
          sum(case when g.name ~ '^......2' then mgd.weightedoccurrences else 0 end) as weighted_plasmepsin2x,
          sum(case when g.name ~ '^.....H2' then mgd.occurrences else 0 end) as occurances_double,
          sum(case when g.name ~ '^.....H2' then mgd.clinicaloccurrences else 0 end) as clinical_double,
          sum(case when g.name ~ '^.....H2' then mgd.weightedoccurrences else 0 end) as weighted_double
        FROM sim.monthlydata md
          INNER JOIN sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
          INNER JOIN sim.genotype g on g.id = mgd.genomeid
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed > (11 * 365)
        GROUP BY md.replicateid, md.dayselapsed) as genotypes on (genotypes.dayselapsed = monthly.dayselapsed)
      ORDER BY monthly.dayselapsed"""
  return select(CONNECTION, sql, {'replicateId':replicateId})


def merge_data(replicates, path, outfile):
  # Read the first file so we have something to append to
  infile = os.path.join(path, "{}.csv".format(replicates[0]))
  data = pd.read_csv(infile, header=None)

  for replicate in replicates[1:]:
    infile = os.path.join(path, "{}.csv".format(replicate))
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
    # Place the dataset in the correct directory
    directory = DATASET_DIRECTORY
    if 'spike' in configuration:
      directory = SPIKE_DIRECTORY    

    # Filter the replicates and merge the most recent entries for the dataset
    data = replicates[replicates[2] == configuration]
    filename = os.path.join(directory, configuration.replace('yml', 'csv'))
    merge_data(data[-50:][3].to_numpy(), REPLICATE_DIRECTORY, filename)
    count = count + 1
    progressBar(count, len(configurations))


def process_final_datasets(date, path, results):
  print("Preparing data sets...")
  replicates = pd.read_csv(REPLICATES_LIST, header=None)
  configurations = replicates[2].unique()

  for configuration in configurations:
    # Skip the spike configurations
    if 'spike' in configuration: 
      continue

    # Filter the replicates specific to this configuration
    data = replicates[replicates[2] == configuration]
    if date is not None:
      data = data[data[4] > date]
    
    # Scan the replicates returned to make sure the frequency is high enough
    valid = []
    for index, row in data.iterrows():
      filename = "{}/{}.csv".format(path, row[3])

      # If the file doesn't exist, then skip
      if not os.path.exists(filename):
        continue

      if check_replicate(filename):
        valid.append(row[3])

        # Break if we have enough, even if there are still some pending.
        # This may occur when extra replicates are run to me the target.
        if len(valid) == REPLICATE_COUNT: 
          break

    # Merge the files if we have results
    if len(valid) > 0:
      filename = os.path.join(results, configuration.replace('yml', 'csv'))
      merge_data(valid, path, filename)

    # Update the user
    print("{}: {}".format(configuration, len(valid)))


def check_replicate(filename):
  DATES, DISTRICT, INDIVIDUALS, WEIGHTED = 2, 3, 4, 8

  # If this is a genotype data set then it automatically gets a pass
  if 'genotype' in filename:
    return True

  # Load the data, note the unique dates, replicates
  data = pd.read_csv(filename, header = None)
  dates = data[DATES].unique().tolist()
  startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")

  # Scan until the date matches the reference date
  for date in dates:    

    # Verify the frequency if this is the correct date
    currentDate = startDate + datetime.timedelta(days=date)
    if currentDate == rwanda.REFERENCEDATE:
      temp = data[data[DATES] == date]
      temp = temp[temp[DISTRICT] == rwanda.REFERENCEDISTRICT]

      # Return false if the replicate is below the reference frequency
      if (temp[WEIGHTED] / temp[INDIVIDUALS]).values[0] < rwanda.REFERENCEFREQUENCY:
        return False

  # Valid replicate to use
  return True


def process_genotype(date):
  GENOTYPE_DATASET = 'data/genotype_dataset'
  GENOTYPE_DIRECTORY = 'data/genotype'
  FILENAMES = ['rwa-ae-al-5.yml', 
               'rwa-pfpr-constant.yml',
               'rwa-replacement-dhappq.yml', 
               'rwa-mft-asaq-dhappq-0.25.yml',
               'rwa-rotation-al-5.yml',
               'rwa-tact-alaq.yml']

  if not os.path.exists(GENOTYPE_DATASET): os.makedirs(GENOTYPE_DATASET)
  if not os.path.exists(GENOTYPE_DIRECTORY): os.makedirs(GENOTYPE_DIRECTORY)

  print("Querying for replicates list...")
  replicates = get_replicates()
  save_csv(REPLICATES_LIST, replicates)
  
  print("Processing replicates...")  
  count = 0
  progressBar(count, len(replicates))
  for row in replicates:
    # Pass if the replicate is too old or a
    if (row[4].date() < datetime.datetime.strptime(date, '%Y-%m-%d').date()) or (row[2] not in FILENAMES):
      continue

    # Check to see if we already have the data
    filename = os.path.join(GENOTYPE_DIRECTORY, "{}.csv".format(row[3]))
    if os.path.exists(filename): continue

    # Query and store the data
    replicate = get_genotype_replicate(row[3])
    save_csv(filename, replicate)

    # Update the progress bar
    count = count + 1
    progressBar(count, len(replicates))

  # Complete progress bar for replicates
  if count != len(replicates): progressBar(len(replicates), len(replicates))  

  # Merge the data sets
  process_final_datasets(date, GENOTYPE_DIRECTORY, GENOTYPE_DATASET)


# Process the replicates to make sure we have all of the data we need locally
def process_replicates():
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

  # Complete progress bar for replicates
  if count != len(replicates): progressBar(len(replicates), len(replicates))


def save_csv(filename, data):
  with open(filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in data:
      writer.writerow(row)


def main():
  if not os.path.exists(REPLICATE_DIRECTORY): os.makedirs(REPLICATE_DIRECTORY)
  if not os.path.exists(DATASET_DIRECTORY): os.makedirs(DATASET_DIRECTORY)
  if not os.path.exists(SPIKE_DIRECTORY): os.makedirs(SPIKE_DIRECTORY)

  # Download all of the replicate data locally, then we need to pull the 
  # relevant replicates to the side as the data set for plotting. Since the 
  # project is iterating quickly this will save on needing to clean-up the 
  # database.
  process_replicates()

  if MANUSCRIPT: 
    process_final_datasets('2022-06-30', REPLICATE_DIRECTORY, DATASET_DIRECTORY)
  else:
    process_datasets()


if __name__ == '__main__':
#  main()
  process_genotype('2022-06-30')