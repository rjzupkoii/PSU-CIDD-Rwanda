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

def get_replicate(replicateId):
  sql = """
        SELECT one.location as district,
          round(two.clinical / (one.population / 1000.0), 2) as incidence,
          round(cast(two.pfpr_numerator / one.population as numeric), 2) as pfpr
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
          sum(msd.clinicalepisodes) as clinical,
          sum(msd.pfpr2to10 * msd.population) as pfpr_numerator
        FROM sim.monthlydata md 
          INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed between 6209 and 6544
        GROUP BY md.replicateid, msd.location) two 
        ON one.replicateid = two.replicateid AND one.location = two.location
        ORDER BY one.location
        """
  return db.select(CONNECTION, sql, {'replicateId': replicateId})


def generate(df, by, percentage):
  # Sort the data and prepare the data structure
  df.sort_values(by=[by], ascending=False)
  top, bottom = [], []

  # Allocate the top, bottom
  target, count = int(round(len(df) * percentage, 0)), 0
  for index, row in df.iterrows():
    if count < target:
      top.append(row.district)
      count += 1
    else:
      bottom.append(row.district)

  # Write the results
  with open(FILENAME, 'a') as out:
    out.write('# Top {:.0%} by {}\n'.format(percentage, by))
    out.write('allocation:\n')
    out.write('\ttop: {}\n'.format(top))
    out.write('\tbottom: {}\n'.format(bottom))


def main(args):
  # Read the replicate into a data frame
  df = pd.DataFrame(columns=['district', 'incidence', 'pfpr'])
  for row in get_replicate(int(args.replicate)):
    df = df.append({'district': row[0], 'incidence': row[1], 'pfpr': row[2]}, ignore_index=True)

  # Prepare configurations for the top 25%, 50%, 75%
  for percentile in [0.25, 0.5, 0.75]:
    generate(df, 'incidence', percentile)
    generate(df, 'pfpr', percentile)


if __name__ == "__main__":
  # Parse the argument
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', action='store', dest='replicate', help='The replicate id to use ')
  args = parser.parse_args()

  # Run the main script
  main(args)
  