#!/usr/bin/env python3

# rwa_district_plot.py
#
# Generate a "dashboard" style plot with the key metrics for each district in Rwanda.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity

STUDYDATE = '2003-1-1'
DISTRICTS = {
    3  : 'Kayonza', 
    8  : 'Gasabo',
    9  : 'Kicukiro',
    10 : 'Nyarugenge',
    17 : 'Hyue'
}

STRUCTURE = {
    'cases': [5, 0, 0, 'Clinical Cases'],
    'failures': [9, 1, 0, 'Treatment Failures'], 
    'frequency' : [-1, 0, 1, '561H Frequency'],
    'carriers': [10, 1, 1, 'Individuals with 561H Clones']
}

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
        for key in STRUCTURE:
            districtData[district][key] = []
        districtData[district]['frequency'] = []

    # Start by filtering by the replicate
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Load the relevent data for each district
        for district in DISTRICTS:
            byDistrict = byReplicate[byReplicate[DISTRICT] == district]

            # Load the simple data
            for key in STRUCTURE:
                if key != 'frequency':
                    # Append the basic information
                    index = STRUCTURE[key][0]
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


dates, data = prepare('data/rwa-mft-al-dhappq-0.25.csv')

# Format the dates
startDate = datetime.datetime.strptime(STUDYDATE, "%Y-%m-%d")
dates = [startDate + datetime.timedelta(days=x) for x in dates]

for district in DISTRICTS:
    # Prepare the plots
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(2, 2)

    for key in STRUCTURE:
        row, col = STRUCTURE[key][1], STRUCTURE[key][2]

        # Load the data and calculate the bounds        
        upper = np.percentile(data[district][key], 97.5, axis=0)
        median = np.percentile(data[district][key], 50, axis=0)
        lower = np.percentile(data[district][key], 2.5, axis=0)

        # Add the data to the subplot
        axes[row, col].plot(dates, median)
        color = scale_luminosity(axes[row, col].lines[-1].get_color(), 1)
        axes[row, col].fill_between(dates, lower, upper, alpha=0.5, facecolor=color)

        # Label the axis as needed
        axes[row, col].set(ylabel = STRUCTURE[key][3])
        if row == 1:
            axes[row, col].set(xlabel = 'Model Year')

    # Format the subplots
    for ax in axes.flat:
        ax.set_xlim([min(dates), max(dates)])

    # Format the overall plot
    figure.suptitle('{}, Rwanda'.format(DISTRICTS[district]))

    plt.savefig('plots/working-{}.png'.format(DISTRICTS[district]))