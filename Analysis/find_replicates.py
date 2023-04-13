#!/usr/bin/env python3

# find_replicates.py
# 
# Find replicates that approximate the mean and IQR provided.
#
# NOTE This script can only be run after data is cached by the 
#      rwa_national_plot.py script.
import csv
import numpy as np
import os
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from database import select

# Number of replicates to report
COUNT = 5

# The offset is the last month, ten years after intervention
OFFSET = 12

# The path for the cache file created by rwa_national_plot.py
CACHE_FILE = '../Ploting/np/violin-cache-2024-10-all.npy'

# Connection string for the database
CONNECTION = 'host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim connect_timeout=60'

# The path to the data sets, genotype outputs
DATASET_PATH = 'ms_data/2024/datasets/'
GENOTYPE_PATH = 'data/heatmaps/'

PLOTS = [
    'rwa-pfpr-constant.csv',            # AL (3-day course)
    'rwa-ae-al-5.csv',                  # AL (5-day course)
    'rwa-replacement-dhappq.csv',       # DHA-PPQ
    'rwa-mft-asaq-dhappq-0.25.csv',     # ASAQ (75%) + DHA-PPQ (25%)
    'rwa-tact-alaq.csv',                # ALAQ
    'rwa-seq-al-asaq.csv',              # AL then ASAQ (456)
    'rwa-rotation-al-5.csv',            # DHA-PPQ three years, then AL (5-day course) + ASAQ
    'rwa-mft-al-dhappq-0.25.csv'        # AL (75%) + DHA-PPQ (25%)
]

# Get the percentile data from the cache file
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


def load_data(report, type, postfix):
    HEADER = ["replicateid","dayselapsed","year","name","frequency"]

    for row in report:
        replicate = int(row.split(',')[1].strip())
        data = select_frequencies(replicate)
        filename = os.path.join(GENOTYPE_PATH, '{}_{}_{}.csv'.format(type, postfix, replicate))
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(HEADER)
            for row in data:
                writer.writerow(row)
        print('Saved {}...'.format(filename))


# Scan the replicate data to see if it is within the relevant bounds
def scan(filename, lower, mean, upper):
    REPLICATE, DATES,  INDIVIDUALS, WEIGHTED = 1, 2, 4, 8
    
    # Load the data
    dataset = pd.read_csv(os.path.join(DATASET_PATH, filename), header = None)

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

    # If the dataset is one that we are going to plot, then get the data and save it
    if filename in PLOTS:
        load_data(report_mean, filename.replace('.csv', ''), 'mean')
        if len(report_lower) > 0:
            load_data(report_lower, filename.replace('.csv', ''), 'lower')
        if len(report_upper) > 0:
            load_data(report_upper, filename.replace('.csv', ''), 'upper')        
    else:
        print(filename)
        print('Lower: {:.5f} - {:.5f} / Mean: {:.5f} - {:.5f} / Upper: {:.5f} - {:.5f}'.format(
            lower[0], lower[1], mean[0], mean[1], upper[0], upper[1]))
        print('Lower ({}): {}'.format(len(report_lower), '; '.join(report_lower)))
        print('Mean  ({}): {}'.format(len(report_mean), '; '.join(report_mean)))
        print('Upper ({}): {}\n'.format(len(report_upper), '; '.join(report_upper)))


# Get the relevant genotype data from the database
def select_frequencies(replicate):
    sql = """
    SELECT replicateid, dayselapsed, year, substring(g.name, 1, 7) as name, frequency
    FROM (
        SELECT mgd.replicateid, mgd.genomeid, mgd.dayselapsed, 
            TO_CHAR(TO_DATE('2003-01-01', 'YYYY-MM-DD') + interval '1' day * mgd.dayselapsed, 'YYYY') AS year,
            mgd.weightedoccurrences / msd.infectedindividuals AS frequency
        FROM (
            SELECT md.replicateid, md.id, md.dayselapsed, mgd.genomeid, sum(mgd.weightedoccurrences) AS weightedoccurrences
            FROM sim.monthlydata md INNER JOIN sim.monthlygenomedata mgd ON mgd.monthlydataid = md.id
            WHERE md.replicateid = %(replicate)s AND md.dayselapsed > 4015
            GROUP BY md.id, md.dayselapsed, mgd.genomeid) mgd
        INNER JOIN (
            SELECT md.id, sum(msd.infectedindividuals) AS infectedindividuals
            FROM sim.monthlydata md INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
            WHERE md.replicateid = %(replicate)s AND md.dayselapsed > 4015
            GROUP BY md.id) msd 
        ON msd.id = mgd.id) frequency inner join sim.genotype g on g.id = frequency.genomeid"""
    return select(CONNECTION, sql, {'replicate': replicate})


if __name__ == '__main__':
    percentiles = get_percentiles(CACHE_FILE)
    for key in percentiles.keys():
        scan(key, percentiles[key][0], percentiles[key][1], percentiles[key][2])
