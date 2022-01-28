#!/usr/bin/env python3

# rwa_district_plot.py
#
# Generate a "dashboard" style plot with the key metrics for each district in Rwanda.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys

import rwanda

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
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
        districtData[district]['frequency'] = []

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
    # Format the dates
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]

    for district in rwanda.DISTRICTS:
        # Prepare the plots
        matplotlib.rc_file('matplotlibrc-line')
        figure, axes = plt.subplots(2, 2)

        for key in rwanda.REPORT_LAYOUT:
            row, col = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_ROW], rwanda.REPORT_LAYOUT[key][rwanda.REPORT_COLUMN]

            # Load the data and calculate the bounds        
            data = districtData[district][key]
            upper = np.percentile(data, 97.5, axis=0)
            median = np.percentile(data, 50, axis=0)
            lower = np.percentile(data, 2.5, axis=0)

            # Add the data to the subplot
            axes[row, col].plot(dates, median)
            color = scale_luminosity(axes[row, col].lines[-1].get_color(), 1)
            axes[row, col].fill_between(dates, lower, upper, alpha=0.5, facecolor=color)

            # Label the axis as needed
            plt.sca(axes[row, col])
            plt.ylabel(rwanda.REPORT_LAYOUT[key][rwanda.REPORT_YLABEL])

            if row == 1:
                plt.xlabel('Model Year')

        # Format the subplots
        for ax in axes.flat:
            ax.set_xlim([min(dates), max(dates)])

        # Format the overall plot
        figure.suptitle('{}\n{}, Rwanda'.format(title, rwanda.DISTRICTS[district]))

        # Save the plot
        os.makedirs('plots/{}'.format(title), exist_ok=True)
        plt.savefig('plots/{0}/{1} - {0}.png'.format(title, rwanda.DISTRICTS[district]))
        plt.close()

        # Update the progress bar
        progressBar(district, len(rwanda.DISTRICTS))


if __name__ == '__main__':
    main()