#!/usr/bin/env python3

# rwa_561H_plot.py
#
# Plot the 561H validation replicates, within spiking studies labeled.
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
    print('Parsing 561H verification data ...')
    os.makedirs('plots', exist_ok=True)
    filename = os.path.join(rwanda.DATA_PATH, 'rwa-561h-verification.csv')
    plot_validation(filename, 'plots/561H Verification.png')
    filename = os.path.join(rwanda.DATA_PATH, 'rwa-spike.csv')
    plot_validation(filename, 'plots/561H Spikes.png')

    for filename in rwanda.CONFIGURATIONS:
        print('Parsing {} ...'.format(filename))
        results = prepare_national(os.path.join(rwanda.DATA_PATH, filename))
        rwanda.plot_summary(rwanda.CONFIGURATIONS[filename], *results)   


def prepare_national(filename):
    REPLICATE, DATES, INDIVIDUALS, WEIGHTED = 1, 2, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Build the dictionary for the results
    results = {}
    for key in rwanda.REPORT_LAYOUT:
        results[key] = []

    # Start by filtering by the replicate
    count = 0
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Prepare the data structure for this replicate
        values = {}
        for key in rwanda.REPORT_LAYOUT:
            values[key] = []

        # Next, filter by date so we can properly aggregate
        for date in dates:           
            byDate = byReplicate[byReplicate[DATES] == date]
            for key in rwanda.REPORT_LAYOUT:
                if key != 'frequency':
                    index = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_INDEX]
                    values[key].append(sum(byDate[index]))
                else:
                    values[key].append(sum(byDate[WEIGHTED]) / sum(byDate[INDIVIDUALS]))

        # Append this replicate to our results
        for key in rwanda.REPORT_LAYOUT:
            if len(results[key]) != 0:
                results[key] = np.vstack((results[key], values[key]))
            else:
                results[key] = values[key]

        # Update the progress bar
        count += 1
        progressBar(count, len(replicates))

    # Return the results
    return dates, results


def prepare_validation(filename):
    REPLICATE, DATES, INDIVIDUALS, WEIGHTED = 1, 2, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Calculate the 561H frequency for each date, replicate
    count, frequencies = 0, []
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]
        frequency = []
        for date in dates:
            byDate = byReplicate[byReplicate[DATES] == date]
            frequency.append(sum(byDate[WEIGHTED]) / sum(byDate[INDIVIDUALS]))
        if len(frequencies) != 0: frequencies = np.vstack((frequencies, frequency))
        else: frequencies = frequency

        # Update the progress bar
        count += 1
        progressBar(count, len(replicates))

    # Return the results
    return dates, frequencies


def plot_validation(datafile, imagefile):
    # Prepare the data
    dates, frequencies = prepare_validation(datafile)

    # Format the dates
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]

    # Calculate the bounds
    upper = np.percentile(frequencies, 97.5, axis=0)
    median = np.percentile(frequencies, 50, axis=0)
    lower = np.percentile(frequencies, 2.5, axis=0)

    # Format the plot
    matplotlib.rc_file('matplotlibrc-line')
    axes = plt.axes()
    axes.set_xlim([min(dates), max(dates)])
    axes.set_title('Rwanda 561H Frequency Validation')
    axes.set_ylabel('561H Genotype Frequency')
    axes.set_xlabel('Model Year')

    # Plot the 561H frequency
    plt.plot(dates, median)
    color = scale_luminosity(plt.gca().lines[-1].get_color(), 1)
    plt.fill_between(dates, lower, upper, alpha=0.5, facecolor=color)

    # Add the spike annotations
    plt.scatter(rwanda.SPIKES[:, rwanda.SPIKE_X], rwanda.SPIKES[:, rwanda.SPIKE_Y], color='black', s=50)
    for district, label, x, y in rwanda.SPIKES:
        plt.annotate(label, (x, y), textcoords='offset points', xytext=(0,10), ha='center', fontsize=18)

    # Finalize the image as proof (png) or print (tif)
    if imagefile.endswith('tif'):
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    else:
        plt.savefig(imagefile)
    plt.close()


if __name__ == '__main__':
    main()