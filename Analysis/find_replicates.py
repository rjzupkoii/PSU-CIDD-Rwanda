#!/usr/bin/env python3

# find_replicates.py
# 
# Find replicates that approximate the mean and IQR provided.
#
# NOTE This script can only be run after data is cached by the 
#      rwa_nationa_plot.py script.
import numpy as np
import os
import pandas as pd
import sys

# Number of replicates to report
COUNT = 3

# The offset is the last month, ten years after intervention
OFFSET = 12

# The path for the cache file created by rwa_national_plot.py
CACHE_FILE = 'np/violin-cache-2024-10-all.npy'

# The path to the data sets
PATH = '../Analysis/ms_data/2024/datasets/'

def get_percentiles(filename):

    # Verify that the cache exists
    if not os.path.isfile(filename):
        print('Cache file {} does not exist!'.format(filename))
        sys.exit(1)

    # Load the cache file
    data = np.load(filename, allow_pickle=True)
    data = dict(enumerate(data.flatten(), 0))[0]

    # Generate a dictionary of files and the percentiles
    results = {}
    for key in data.keys():
        frequency = []
        for row in data[key]['frequency']:
            frequency.append(row[-1])
        results[key] = np.percentile(frequency, [25, 50, 75])
    return results


def scan(filename, lower, mean, upper):
    REPLICATE, DATES,  INDIVIDUALS, WEIGHTED = 1, 2, 4, 8
    
    # Load the data
    dataset = pd.read_csv(os.path.join(PATH, filename), header = None)

    # Calculate the bounds
    lower = [lower, lower * 1.025]
    mean = [mean * 0.975, mean * 1.025]
    upper = [upper * 0.975, upper]

    # Find the date bounds for five years post implementation
    date = dataset[DATES].unique().tolist()[-OFFSET]

    # Track the counts
    report_lower, report_mean, report_upper = [], [], []

    # Iterate through the replicates
    replicates = dataset[REPLICATE].unique().tolist()
    for replicate in replicates:
       
        # Find the national frequency the given month
        data = dataset[dataset[REPLICATE] == replicate]
        data = data[data[DATES] == date]
        frequency = sum(data[WEIGHTED]) / sum(data[INDIVIDUALS])

        # Report the replicates as they are found
        if lower[0] <= frequency and frequency <= lower[1]:
            if len(report_lower) == COUNT: continue
            report_lower.append('{:.4f}, {}'.format(frequency, replicate))
        elif mean[0] <= frequency and frequency <= mean[1]:
            if len(report_mean) == COUNT: continue
            report_mean.append('{:.4f}, {}'.format(frequency, replicate))
        elif upper[0] <= frequency and frequency <= upper[1]:
            if len(report_upper) == COUNT: continue
            report_upper.append('{:.4f}, {}'.format(frequency, replicate))

    # Print the results
    print(filename)
    print('Lower: {:.5f} - {:.5f} / Mean: {:.5f} - {:.5f} / Upper: {:.5f} - {:.5f}'.format(
        lower[0], lower[1], mean[0], mean[1], upper[0], upper[1]))
    print('Lower ({}): {}'.format(len(report_lower), '; '.join(report_lower)))
    print('Mean  ({}): {}'.format(len(report_mean), '; '.join(report_mean)))
    print('Upper ({}): {}\n'.format(len(report_upper), '; '.join(report_upper)))

if __name__ == '__main__':
    percentiles = get_percentiles(CACHE_FILE)
    for key in percentiles.keys():
        scan(key, percentiles[key][0], percentiles[key][1], percentiles[key][2])
