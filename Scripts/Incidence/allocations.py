#!/usr/bin/python3

# allocations.py
#
# Generate the allocations for drug policy interventions based upon the projected
# incidence, PfPR, and 561H frequency by district.
import argparse
import os
import pandas as pd

import sys

# Import our libraries
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import database as db

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# The filename that the results are written to
FILENAME = 'results.yml'


# Return all of the replicate data for the given configuration and model days elapsed.
# 
# Sample data - configuration: 11429, startdate: 7701, enddate: 8036
def get_status_quo(configurationid, startdate, enddate, genotype='^.....H.'):
  sql = """
        SELECT one.id, one.location, 
          round(one.incidence, 2) AS incidence,
          round(CAST(one.pfpr2to10 AS numeric), 2) AS pfpr2to10,
          round(CAST(two.weightedoccurrences / one.infectedindividiuals AS numeric), 4) AS frequency
        FROM (
          SELECT r.id, msd.location,
            sum(msd.infectedindividuals) AS infectedindividiuals,
            sum(msd.clinicalepisodes) / (sum(msd.population) / 1000.0) AS incidence,
            sum(msd.pfpr2to10 * msd.population) / sum(msd.population) AS pfpr2to10
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


def generate(df, by, percentage):
  # Sort the data and prepare the data structure
  df = df.sort_values(by=[by], ascending=False)
  top, bottom = [], []

  # Allocate the top, bottom
  target, count = int(round(len(df) * percentage, 0)), 0
  for index, row in df.iterrows():
    if count < target:
      top.append(int(row.district))
      count += 1
    else:
      bottom.append(int(row.district))

  # Write the results
  with open(FILENAME, 'a') as out:
    out.write('# Top {:.0%} by {}\n'.format(percentage, by))
    out.write('allocation:\n')
    out.write('\ttop: {}\n'.format(top))
    out.write('\tbottom: {}\n'.format(bottom))


def main(args):
  # Get the reference frequency data
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
      'frequency': row[4]
    }, ignore_index=True)
  
  # Filter out all of the replicates with a frequency above our reference
  ids = frequencies[frequencies.frequency > args['threshold']].replicate
  replicates = replicates[replicates.replicate.isin(ids)]

  # Let the user know the number of replicates we are using for the median
  print('Using {} replicates to compute median district values...'.format(len(replicates.replicate.unique())))

  # Compute the median for each of the districts
  districts = pd.DataFrame(columns=['district', 'incidence', 'pfpr2to10', 'frequency'])
  for id in replicates.district.unique():
    filtered = replicates[replicates.district == id]
    districts = districts.append({
      'district': id,
      'incidence': filtered.median().incidence,
      'pfpr2to10': filtered.median().pfpr2to10,
      'frequency': filtered.median().frequency
    }, ignore_index=True)

  # Prepare configurations for the top 25%, 50%, 75%
  print('Computing configurations...')
  for percentile in [0.25, 0.5, 0.75]:
    generate(districts, 'incidence', percentile)
    generate(districts, 'pfpr2to10', percentile)
    generate(districts, 'frequency', percentile)


if __name__ == "__main__":
  # Default arguments for testing
  args = {
    'configuration': 11429, 'startdate': 7701, 'enddate': 8036,
    'location': 8, 'dayselapsed': 4261, 'threshold': 0.01
  }

  # Run the main script
  main(args)
  