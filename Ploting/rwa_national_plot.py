#!/usr/bin/env python3

# rwa_561H_plot.py
#
# Plot the 561H validation replicates, within spiking studies labeled.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity


# Settings that are passed to the plot function
DATAFILE = 'data/rwa-561h-verification.csv'
IMAGEFILE = 'rwa-spike-verification.png'


def prepare(filename):
    REPLICATE, DATES, INDIVIDUALS, WEIGHTED = 1, 2, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Calculate the 561H frequency for each date, replicate
    frequencies = []
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]
        frequency = []
        for date in dates:
            byDate = byReplicate[byReplicate[DATES] == date]
            frequency.append(sum(byDate[WEIGHTED]) / sum(byDate[INDIVIDUALS]))
        if len(frequencies) != 0: frequencies = np.vstack((frequencies, frequency))
        else: frequencies = frequency

    # Return the results
    return dates, frequencies


def plot(datafile, imagefile):
    STUDYDATE = '2003-1-1'
    SPIKES = np.array([
        # Uwimana et al. 2020 
        ['Gasabo (0.12069)', datetime.datetime(2014,9,30), 0.12069],
        ['Kayonza (0.00746)', datetime.datetime(2015,9,30), 0.00746],
        ['Gasabo (0.0603)', datetime.datetime(2015,9,30), 0.0603],
        
        # Uwimana et al. 2021
        ['Gasabo (0.19608)', datetime.datetime(2018,9,30), 0.19608],
        ['Kayonza (0.09756)', datetime.datetime(2018,9,30), 0.09756],

        # Straimer et al. 2021
        ['Kigali City (0.21918)', datetime.datetime(2019,9,30), 0.21918],

        # Bergmann et al. 2021 
        ['Hyue (0.12069)', datetime.datetime(2019,9,30), 0.12121],
    ])
    
    # Prepare the data
    dates, frequencies = prepare(datafile)

    # Format the dates
    startDate = datetime.datetime.strptime(STUDYDATE, "%Y-%m-%d")
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
    plt.scatter(SPIKES[:, 1], SPIKES[:, 2], color='black', s=50)
    for label, x, y in SPIKES:
        plt.annotate(label, (x, y), textcoords='offset points', xytext=(0,10), ha='center', fontsize=18)

    # Finalize the image as proof (png) or print (tif)
    if imagefile.endswith('tif'):
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    else:
        plt.savefig(imagefile)
    plt.close()


if __name__ == '__main__':
    plot(DATAFILE, IMAGEFILE)    