#!/usr/bin/python3

# extract.py
#
# Restore the YAML files that were run by processing the YAML strings in the 
# CSV files. This script assumes that the files are present in data/ and the
# CSV was generated via the relevant query in queries.sql
import csv
import os

SENTINEL = chr(1)
FILENAME, STUDY, YAML = 2, 3, 4

os.makedirs('out', exist_ok=True)
with open('data/rwanda-interventions-yaml.csv') as input:
    # Start the reader and skip the header
    reader = csv.reader(input)
    next(reader)

    # Process the remaining rows
    for row in reader:

        # Create the path for the YAML
        path = os.path.join('out', row[STUDY])
        os.makedirs(path, exist_ok=True)
        
        # Write the YAML to the file
        text = row[YAML].replace(SENTINEL, '\n')
        with open(os.path.join(path, row[FILENAME]), 'w') as output:
            output.write(text)
