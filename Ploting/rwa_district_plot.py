#!/usr/bin/env python3

# rwa_district_plot.py
#
# Generate a "dashboard" style plot with the key metrics for each district in Rwanda.
import numpy as np
import os
import pandas as pd
import sys

import rwanda

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from utility import progressBar

def main():
    for filename in rwanda.CONFIGURATIONS:
        print('Parsing {} ...'.format(filename))
        results = prepare(os.path.join('../Analysis/data/datasets', filename))
        report(rwanda.CONFIGURATIONS[filename], *results)    


def prepare(filename):
    REPLICATE, DATES, DISTRICT, INDIVIDUALS, WEIGHTED = 1, 2, 3, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Build the dictionary that will be used to store data
    districtData = {}
    for district in rwanda.DISTRICTS:
        districtData[district] = {}
        for key in rwanda.REPORT_LAYOUT:
            districtData[district][key] = []

    # Start by filtering by the replicate
    count = 0
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Load the relevent data for each district
        for district in rwanda.DISTRICTS:
            byDistrict = byReplicate[byReplicate[DISTRICT] == district]

            # Load the simple data
            for key in rwanda.REPORT_LAYOUT:
                if key != 'frequency':
                    # Append the basic information
                    index = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_INDEX]
                    if len(districtData[district][key]) != 0:
                        districtData[district][key] = np.vstack((districtData[district][key], byDistrict[index]))
                    else:
                        districtData[district][key] = byDistrict[index]
                else:
                    # Append the 561H frequency data
                    frequency = byDistrict[WEIGHTED] / byDistrict[INDIVIDUALS]
                    if len(districtData[district][key]) != 0:
                        districtData[district][key] = np.vstack((districtData[district][key], frequency))
                    else:
                        districtData[district][key] = frequency

        # Update the progress bar
        count += 1
        progressBar(count, len(replicates))
    
    # Return the results
    return dates, districtData


def report(title, dates, districtData):
    for district in rwanda.DISTRICTS:
        rwanda.plot_summary(title, dates, districtData[district], district=district)
        progressBar(district, len(rwanda.DISTRICTS))


if __name__ == '__main__':
    main()