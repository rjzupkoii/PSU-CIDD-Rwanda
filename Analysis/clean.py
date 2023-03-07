#!/usr/bin/python3

# clean.py
#
# Clean-up the local replicate files in data/replicates that aren't needed.
import os
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from database import select

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# The path the files are stored in by default
PATH = 'data/replicates'


def get_replicates():
    sql = """
        SELECT c.id AS configurationid, c.studyid, r.id
        FROM sim.configuration c
          INNER JOIN sim.replicate r on r.configurationid = c.id
        WHERE c.studyid IN (19, 20, 21, 22)
          AND r.starttime > to_date('2023-01-01', 'YYYY-MM-DD')"""
    return select(CONNECTION, sql, None)

def main():
    # Load the replicates from the database
    replicates = []
    for row in get_replicates():
        replicates.append('{}.csv'.format(row[2]))
    
    # Load the replicates from the file system
    files = os.listdir(PATH)
    
    # Check the file system replicates to see if the should be deleted
    count = 0
    for file in files:
        if file not in replicates:
            os.remove(os.path.join(PATH, file))
            count += 1

    print('Cached replicates deleted:', count) 


if __name__ == '__main__':
    main()