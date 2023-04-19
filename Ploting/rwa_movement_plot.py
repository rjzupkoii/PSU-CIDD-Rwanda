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
import re
import sys

import rwanda

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
from utility import progressBar

def main(extension):
    root = '../Analysis/ms_data/'
    filenames = [
        '2024/datasets/rwa-pfpr-constant.csv',
        'sensitivity/rwa-movement-0.3x.csv',
        'sensitivity/rwa-movement-0.5x.csv',
        'sensitivity/rwa-movement-2x.csv',
        'sensitivity/rwa-movement-3x.csv',
        'sensitivity/rwa-fitness-10x.csv',
        'sensitivity/rwa-fitness-25x.csv',
        'sensitivity/rwa-fitness-50x.csv'
    ]

    os.makedirs('plots', exist_ok=True)

    for filename in filenames:
        # Prepare the filenames
        prefix = 'Movement'; suffix = 'movement rate'
        if 'constant' in filename:
            rate = '1x'
            title = 'National 561H Frequency'
        elif 'movement' in filename:
            rate = filename[25:].replace('.csv', '')
            title = 'National 561H Frequency with {} Increase in Movement'.format(rate)
        else:
            rate = filename[24:].replace('.csv', '')
            prefix = 'Fitness'
            suffix = 'fitness penalty'
            title = 'National 561H Frequency with {} Increase in Fitness Penalty'.format(rate)

        # Verify that the file exists
        filename = os.path.join(root, filename)
        if not os.path.exists(filename): continue
        print('Preparing {} plots...'.format(rate))

        # Start by preparing the national summary plot
        rwanda.plot_validation(filename, 'plots/{} Sensitivity - {}.{}'.format(prefix, rate, extension), title=title)

        # Now prepare the district spiking plot
        plot_spikes(filename, rate, prefix, suffix, extension)


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

        # Load the relevant data for each district
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


def plot_spikes(filename, rate, prefix, suffix, extension):
    LOCATIONS = {
        8: [0, 0], 3: [0, 1], 17: [0, 2],
        4: [1, 0], 5: [1, 1], 
    }
    DHS_DATA = np.array([
        # Kirby et al. 2022
        [4, 'Kirehe (0.056)', datetime.datetime(2015,9,30), 0.05556],
        [5, 'Ngoma (0.019)', datetime.datetime(2015,9,30), 0.01923],
    ])

    # Get the clinical data
    data_points = np.append(rwanda.SPIKES, DHS_DATA, axis=0)
    districts = []
    for row in data_points:
        if row[rwanda.SPIKE_DISTRICT] == 0: continue
        if row[rwanda.SPIKE_DISTRICT] not in districts:
            districts.append(row[rwanda.SPIKE_DISTRICT])

    # Generate the standard four-panel summary plot
    dates, districtData = prepare(filename)
    for id in districts:
        rwanda.plot_summary('District 561H Validation', dates, districtData[id], district=id, studies=True)

    # Format the dates
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]

    # Prepare the plots
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(2, 3)

    # Generate a five panel plot with just the frequency data
    ymax = 0
    for id in districts:
        # Load the data and calculate the bounds      
        if id not in LOCATIONS: continue
        row, col = LOCATIONS[id][0], LOCATIONS[id][1]
        axes[row, col], limit = rwanda.plot_data(districtData[id]['frequency'], dates, axes[row, col])
        axes[row, col].title.set_text(rwanda.DISTRICTS[id])

        # Label the axis as needed
        plt.sca(axes[row, col])
        if col == 0: plt.ylabel('561H Frequency')

        # Add the 561H data points
        for spikeId, label, x, y in data_points:           
            if id == spikeId:
                plt.scatter(x, y, color='black', s=50)
                match = re.search('(\d\.\d*)', label)
                plt.annotate(match.group(0), (x, y), textcoords='offset points', xytext=(0,10), ha='center', fontsize=18)

        # Update our tracking variables
        ymax = max(limit, ymax)

    # Format the subplots, hide the empty subplot
    if ymax > 0.8: ymax = 1.0
    for ax in axes.flat:
        ax.set_ylim([0, ymax])
        ax.set_xlim([datetime.datetime(2014, 1, 1), max(dates)])
    axes[1, 2].set_visible(False)
    
    figure.suptitle('District 561H Frequency with {} {}'.format(rate, suffix))
    
    # Save the plot based upon the supplied extension
    imagefile = 'plots/District {} {}.{}'.format(prefix, rate, extension)
    if 'tif' == extension:
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    elif 'svg' == extension:
        plt.savefig(imagefile, dpi=1200, format="svg")
    else:
        plt.savefig(imagefile, dpi=150)
    plt.close()


if __name__ == '__main__':
    main('png')