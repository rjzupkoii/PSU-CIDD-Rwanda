#!/usr/bin/env python3

# find_replicates.py
# 
# Find replicates that approximate the mean and IQR provided.
import os
import pandas as pd

# Number of replicates to report
COUNT = 3

# The offset is the last month, ten years after intervention
OFFSET = 12

# The path to the data sets
PATH = '../Analysis/ms_data/2024/datasets/'

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
    print('Lower: {} / Mean: {} / Upper: {}'.format(lower, mean, upper))
    print('Lower ({}): {}'.format(len(report_lower), '; '.join(report_lower)))
    print('Mean  ({}): {}'.format(len(report_mean), '; '.join(report_mean)))
    print('Upper ({}): {}\n'.format(len(report_upper), '; '.join(report_upper)))

if __name__ == '__main__':
    scan('rwa-pfpr-constant.csv', 0.9689, 0.9819, 0.9893)
    scan('rwa-ae-al-5.csv', 0.8809, 0.9388, 0.9599)
    scan('rwa-tact-alaq.csv', 0.4125, 0.5183, 0.6552)
    scan('rwa-replacement-dhappq.csv', 0.9983, 0.9989, 0.9993)
    scan('rwa-mft-asaq-dhappq-0.25.csv', 0.8523, 0.9221, 0.9444)
    scan('rwa-seq-al-asaq.csv', 0.5856, 0.7018, 0.7652)