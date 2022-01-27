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

# Disable log10 divide by zero warnings
np.seterr(divide  = 'ignore')

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity

STUDYDATE = '2003-1-1'
DISTRICTS = {
    3  : 'Kayonza',         # Spiked
    8  : 'Gasabo',          # Spiked
    9  : 'Kicukiro',        # Spiked
    10 : 'Nyarugenge',      # Spiked
    14 : 'Musanze', 
    17 : 'Hyue'             # Spiked
}

INDEX, ROW, COLUMN, YLABEL = range(4)
REPORT_FORMAT = {
    'cases': [5, 0, 0, 'Clinical Cases'],
    'failures': [9, 1, 0, 'Treatment Failures'], 
    'frequency' : [-1, 0, 1, '561H Frequency'],
    'carriers': [10, 1, 1, 'Individuals with 561H Clones']
}


def main():
    REPORTS = {
        'rwa-pfpr-constant.csv' : 'Status Quo',
        'rwa-mft-al-dhappq-0.25.csv' : 'MFT AL (75%) + DHA-PPQ (25%)',
    }

    os.makedirs('plots/', exist_ok=True)
    for filename in REPORTS:
        print('Parsing {} ...'.format(filename))
        results = prepare(os.path.join('../Analysis/data/datasets', filename))
        report(REPORTS[filename], *results)    


def prepare(filename):
    REPLICATE, DATES, DISTRICT, INDIVIDUALS, WEIGHTED = 1, 2, 3, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Build the dictionary that will be used to store data
    districtData = {}
    for district in DISTRICTS:
        districtData[district] = {}
        for key in REPORT_FORMAT:
            districtData[district][key] = []
        districtData[district]['frequency'] = []

    # Start by filtering by the replicate
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Load the relevent data for each district
        for district in DISTRICTS:
            byDistrict = byReplicate[byReplicate[DISTRICT] == district]

            # Load the simple data
            for key in REPORT_FORMAT:
                if key != 'frequency':
                    # Append the basic information
                    index = REPORT_FORMAT[key][INDEX]
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
    
    # Return the results
    return dates, districtData


def baseRound(x, base):
    if base == 0: return 0
    return base * np.round(x / base)

def formatYTicks(ticks):
    # Parse out the ticks, note we are discarding anything less than zero
    ticks = ticks[0]
    ticks = ticks[ticks >= 1]

    # Map the ticks to values
    if max(np.floor(ticks)) >= 6:
        labels = np.array(baseRound(10 ** ticks, min(np.floor(ticks)))) / 10 ** 6
        labels = np.array2string(labels, formatter={'float_kind' : lambda value: "{value: .1f}K".format(value = value)})
    else:
        labels = np.array(baseRound(10 ** ticks, min(np.floor(ticks)))) / 10 ** 3
        labels = np.array2string(labels, formatter={'float_kind' : lambda value: "{value: .1f}K".format(value = value)})
    
    # Split the labels out
    labels = labels[1:-1].split()

    # 1) Check for duplicates in the first value, this is a bit of an edge case for low values
    # 2) Clip 0.0K since it results in an odd plot
    if (labels[0] == labels[1]) or (labels[0] == '0.0K'):
        ticks = ticks[1:]
        labels = labels[1:]

    return ticks, labels


def report(title, dates, districtData):
    # Format the dates
    startDate = datetime.datetime.strptime(STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]

    for district in DISTRICTS:
        # Prepare the plots
        matplotlib.rc_file('matplotlibrc-line')
        figure, axes = plt.subplots(2, 2)

        for key in REPORT_FORMAT:
            row, col = REPORT_FORMAT[key][ROW], REPORT_FORMAT[key][COLUMN]

            # Load the data and calculate the bounds        
            data = districtData[district][key]
            # if row == col == 0: 
            #     data = np.log10(data)
            upper = np.percentile(data, 97.5, axis=0)
            median = np.percentile(data, 50, axis=0)
            lower = np.percentile(data, 2.5, axis=0)

            # Add the data to the subplot
            axes[row, col].plot(dates, median)
            color = scale_luminosity(axes[row, col].lines[-1].get_color(), 1)
            axes[row, col].fill_between(dates, lower, upper, alpha=0.5, facecolor=color)

            # Label the axis as needed
            plt.sca(axes[row, col])
            plt.ylabel(REPORT_FORMAT[key][YLABEL])
            # if row == col == 0:
            #     ticks, labels = formatYTicks(plt.yticks())
            #     plt.yticks(ticks, labels)
            if row == 1:
                plt.xlabel('Model Year')

        # Format the subplots
        for ax in axes.flat:
            ax.set_xlim([min(dates), max(dates)])

        # Format the overall plot
        figure.suptitle('{}\n{}, Rwanda'.format(title, DISTRICTS[district]))

        # Save the plot
        plt.savefig('plots/{0} - {1}.png'.format(DISTRICTS[district], title))


if __name__ == '__main__':
    main()