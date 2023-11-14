#!/usr/bin/python3

# allocations.py
#
# Generate the allocations for drug policy interventions based upon the projected
# incidence, PfPR, and 561H frequency by district.
import argparse
import numpy as np
import os
import pandas as pd
import sys

# Import our libraries
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import database as db

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# The filename that the results are written to
FILENAME = 'out/results.yml'

# The file that contains the mapping of the district names to IDs
MAPPING = '../../GIS/rwa_districts.csv'

# The reference incidence data
REFERENCE_INCIDENCE = '../../GIS/rwa_district_incidence_2020.csv'

# Path to the fixed intervention template
FIXED_TEMPLATE = '../../Studies/District Intervention/rwa-fixed-template.yml'

# Path to the replicate job template
REPLICATE_TEMPLATE = '../../Studies/District Intervention/rwa-template.job'


# Return all of the replicate data for the given configuration and model days elapsed.
def get_status_quo(configurationid, startdate, enddate, genotype='^.....H.'):
  sql = """
        SELECT one.id, one.location, 
          round(one.incidence, 2) AS incidence,
          round(CAST(one.pfpr2to10 AS numeric), 2) AS pfpr2to10,
          round(CAST(two.weightedoccurrences / one.infectedindividiuals AS numeric), 4) AS frequency,
          one.clinicalepisodes
        FROM (
          SELECT r.id, msd.location,
            sum(msd.infectedindividuals) AS infectedindividiuals,
            sum(msd.clinicalepisodes) / (max(msd.population) / 1000.0) AS incidence,
            sum(msd.pfpr2to10 * msd.population) / sum(msd.population) AS pfpr2to10,
            sum(msd.clinicalepisodes) as clinicalepisodes
          FROM sim.replicate r
            INNER JOIN sim.monthlydata md ON md.replicateid = r.id
            INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
          WHERE r.configurationid = %(configurationid)s
            AND md.dayselapsed between %(startdate)s and %(enddate)s
          GROUP BY r.id, msd.location) one
        INNER JOIN (
          SELECT r.id, mgd.location, sum(mgd.weightedoccurrences) as weightedoccurrences
          FROM sim.replicate r
          INNER JOIN sim.monthlydata md on md.replicateid = r.id
          INNER JOIN sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
          INNER JOIN sim.genotype g ON g.id = mgd.genomeid
          WHERE r.configurationid = %(configurationid)s
          AND md.dayselapsed BETWEEN %(startdate)s and %(enddate)s
          AND g.name ~ %(genotype)s
          GROUP BY r.id, mgd.location) two ON one.id = two.id AND one.location = two.location
        """
  return db.select(CONNECTION, sql, {'configurationid': configurationid, 'startdate': startdate, 'enddate': enddate, 'genotype': genotype})

# Return all of the replicates and their weighted genotype frequency for the given configuration, default genotype filter is for 561H
def get_frequency(configurationid, dayselapsed, location, genotype='^.....H.'):
  sql = """
        SELECT r.id, SUM(mgd.weightedoccurrences) / msd.infectedindividuals AS frequency
        FROM sim.configuration c 
          INNER JOIN sim.replicate r ON r.configurationid = c.id
          INNER JOIN sim.monthlydata md ON md.replicateid = r.id
          INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
          INNER JOIN sim.monthlygenomedata mgd ON mgd.monthlydataid = md.id
          INNER JOIN sim.genotype g ON g.id = mgd.genomeid
        WHERE c.id = %(configurationid)s
          AND md.dayselapsed = %(dayselapsed)s
          AND msd.location = %(location)s
          AND mgd.location = %(location)s
          AND g.name ~ %(genotype)s
        GROUP BY r.id, msd.infectedindividuals
        """
  return db.select(CONNECTION, sql, {'configurationid': configurationid, 'dayselapsed': dayselapsed, 'location': location, 'genotype': genotype})


# Allocate the districts by the metric and percentage indicated.
def allocate(df, by, percentage, therapies, summarize):
  # Sort the data and prepare the data structure
  df = df.sort_values(by=[by], ascending=False)
  top, bottom = [], []

  ## Version one of the allocations, simple selection of districts
  # # Allocate the top, bottom
  # target, count = int(round(len(df) * percentage, 0)), 0
  # for index, row in df.iterrows():
  #   if count < target:
  #     top.append(int(row.district))
  #     count += 1
  #   else:
  #     bottom.append(int(row.district))

  # Allocate the top, bottom
  target, count = round(np.sum(df.clinical) * percentage, 0), 0
  for index, row in df.iterrows():
    if count < target:
      top.append(int(row.district))
      count += row.clinical
    else:
      bottom.append(int(row.district))

  # Read the template file
  with open(FIXED_TEMPLATE, 'r') as read:
    text = read.read()

  # Update the district allocation
  text = text.replace('#TOP#', '{}'.format(top))
  text = text.replace('#BOTTOM#', '{}'.format(bottom))

  for therapy, value in therapies.items():
    # Update the therapy
    final = text.replace('#TOPTHERAPY#', value[0])
    final = final.replace('#BOTTOMTHERAPY#', value[1])

    # Write the configuration to disk
    filename = 'out/rwa-fixed-{}-{}-{}.yml'.format(by, percentage, therapy)
    with open(filename, 'w') as out:
      out.write(final)

  # Update the YAML file with the summary results
  if not summarize: return
  with open(FILENAME, 'a') as out:
    out.write('# Top {:.0%} by {}\n'.format(percentage, by))
    out.write('allocation:\n')
    out.write('\ttop: {}\n'.format(top))
    out.write('\tbottom: {}\n'.format(bottom))      


# Scan the path provided and generate job files for all of the configurations as 
# well as a CSV file to bootstrap the replicate configurations in the database
# and a second to run all of the replicates
def prepare_replicates(path, studyid, count):
  # Open the various files we will be working with
  bootstrap = open('out/boot.csv', 'w')
  replicates = open('out/replicates.csv', 'w')
  
  # Read the job template
  with open(REPLICATE_TEMPLATE, 'r') as read:
    template = read.read()
  template = template.replace('#STUDYID#', str(studyid))

  # Loop over all of the files in the directory
  for file in os.listdir(path):
    if not file.endswith('.yml'): continue
    filename = file.replace('.yml', '.job')
    bootstrap.write('{},1\n'.format(filename))
    replicates.write('{},{}\n'.format(filename, count))

    # Write the job file out to disk
    job = template.replace('#FILENAME#', file)
    with open('out/{}'.format(filename), 'w') as out:
      out.write(job)

  # Clean-up the open files
  bootstrap.close()
  replicates.close()


# Load the status quo replicates from the database and calculate the median values
def process(args):
  # Get the reference frequency data
  print('Loading and checking status quo data...', end='')
  sys.stdout.flush()
  frequencies = pd.DataFrame(columns=['replicate', 'frequency'])
  for row in get_frequency(args['configuration'], args['dayselapsed'], args['location']):
    frequencies = frequencies.append({'replicate': row[0], 'frequency': row[1]}, ignore_index=True)
  
  # Get the status quo data
  replicates = pd.DataFrame(columns=['replicate', 'district', 'incidence', 'pfpr2to10', 'frequency'])
  for row in get_status_quo(args['configuration'], args['startdate'], args['enddate']):
    replicates = replicates.append({
      'replicate': row[0],
      'district': row[1],
      'incidence': row[2],
      'pfpr2to10': row[3],
      'frequency': row[4],
      'clinical': row[5]
    }, ignore_index=True)
  
  # Filter out all of the replicates with a frequency above our reference
  ids = frequencies[frequencies.frequency > args['threshold']].replicate
  replicates = replicates[replicates.replicate.isin(ids)]

  # Compute the median for each of the districts
  districts = pd.DataFrame(columns=['district', 'incidence', 'pfpr2to10', 'frequency'])
  for id in replicates.district.unique():
    filtered = replicates[replicates.district == id]
    districts = districts.append({
      'district': id,
      'incidence': filtered.median().incidence,
      'pfpr2to10': filtered.median().pfpr2to10,
      'frequency': filtered.median().frequency,
      'clinical': np.sum(filtered.clinical)
    }, ignore_index=True)

  # Return the results for the districts
  print(' {} replicates loaded.'.format(len(replicates.replicate.unique())))
  return districts


# Print the summary metrics for each fo the districts 
def summarize(df):
  # Prepare the summary table
  summary = df.astype({'district': 'int'})
  summary = summary.rename(columns={'district': 'ID', 'incidence': 'Incidence', 'pfpr2to10': 'PfPR 2-10', 'frequency': '561H Frequency'})

  # Read the district names
  names = pd.read_csv(MAPPING)
  names = names.rename(columns={'DISTRICT': 'ID', 'NAME': 'District'})

  # Join the names, reorder the columns, and print
  summary['District'] = summary.ID.map(names.set_index('ID')['District'])
  summary = summary.sort_values(by=['District'])
  cols = summary.columns.tolist()
  cols = cols[-1:] + cols[:-1]
  summary = summary[cols]
  print(summary.to_string(index=False))


def validate(df, tolerance = 0.1):
  PASS = '\033[92m'
  FAIL = '\033[91m'
  CLEAR = '\033[0m'

  # Read the reference data, compute the bounds
  reference = pd.read_csv(REFERENCE_INCIDENCE)
  reference['lower'] = reference['Incidence'] * (1 - tolerance)
  reference['upper'] = reference['Incidence'] * (1 + tolerance)
  
  # Join the median incidence to the reference data
  reference['computed'] = reference.OBJECTID.map(df.set_index('district')['incidence'])
  reference = reference.sort_values(by=['ADM2_EN'])

  # Print the summary results
  print("\n{:11}: {:6} v. {:6}".format('District', '  Ref.', 'Proj.'))
  count, failed = 0, 0
  for index, row in reference.iterrows():
    status = PASS + 'PASS' + CLEAR
    if row.computed < row.lower or row.computed > row.upper:
      failed += 1
      status = FAIL + 'FAIL' + CLEAR    
    count += 1
    print("{:11}: {:6} v. {:6} [{}]".format(row.ADM2_EN, row.Incidence, row.computed, status))
  print('{} passing districts out of {}, with ±{:.1%}\n'.format(count - failed, count, tolerance))


def main(args, showValidation, showSummary):
  # TODO Update the script to take command line arguments and parse them into a dictionary

  # Load the district data from the database
  df = process(args)
  if showValidation: validate(df)

  # Generate the allocations and prepare a summary report
  if os.path.isfile(FILENAME): os.unlink(FILENAME)
  os.makedirs('out', exist_ok=True) 
  for percentile in [0.25, 0.5, 0.75]:
    allocate(df, 'incidence', percentile, args['therapies'], showSummary)
    allocate(df, 'pfpr2to10', percentile, args['therapies'], showSummary)
    allocate(df, 'frequency', percentile, args['therapies'], showSummary)
  if showSummary: summarize(df)

  # Generate the relevant replicate scripts
  prepare_replicates('out', parameters['studyid'], parameters['replicates'])

if __name__ == "__main__":
  # TODO Shift these to arguments, for now set default arguments for testing
  parameters = {
    'configuration': 11429, 'startdate': 7701, 'enddate': 8036,
    'location': 8, 'dayselapsed': 4261, 'threshold': 0.01,
    'replicates': 74
  }

  # TODO Shift these to a configuration file
  parameters['therapies'] = {
    'al': ['[0]', '[3]'],
    'dhappq': ['[3]', '[0]']
  }

  # Parse the command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', action='store', dest='studyid', required=True, help='Study ID to assign the jobs')
  parser.add_argument('--summarize', action='store_true', dest='summarize', help='Include to print the median district values')
  parser.add_argument('--validate', action='store_true', dest='validate', help='Include to print the validation information')
  args = parser.parse_args()

  # Run the main script
  parameters['studyid'] = int(args.studyid)
  main(parameters, args.validate, args.summarize)
  