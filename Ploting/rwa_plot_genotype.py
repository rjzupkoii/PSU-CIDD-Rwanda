#!/usr/bin/env python3

# rwa_plot_genotype.py
#
# 
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

import rwanda

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
from utility import progressBar

REPLICATE, DATES, INFECTIONS, TREATMENTS, FAILURES = 0, 1, 3, 5, 6
LAYOUT = {
    'tf' : [-1],
    'pfpr' : [7],
    'freq_561h' : [10],
    'freq_plasmepsin' : [13],
    'freq_double' : [16]
}


# Load all of the files that have been provided
def load(filenames):
    results = {}
    for filename in filenames:
        dates, result = parse(filename)
        results[filename] = result
    return dates, results
    

# Load a single file that contains genotype data
def parse(filename):
    # Load the data and parse out the common data
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Note the project state date
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")

    # Prepare the results data structure
    results = {}
    for key in LAYOUT: results[key] = []

    # Iterate over each of the replicates
    count = 0
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Prepare the data structure for this replicate
        values = {}
        for key in LAYOUT: values[key] = []

        for date in dates:
            # Continue if we haven't got to the intervention date 
            currentDate = startDate + datetime.timedelta(days=date)
            if currentDate < rwanda.POLICYDATE: continue

            # Append the data for this date
            byDate = byReplicate[byReplicate[DATES] == date]
            for key in LAYOUT:
                if 'freq_' in key:
                    values[key].append(byDate[LAYOUT[key][0]] / byDate[INFECTIONS])
                elif 'tf' is key:
                    values[key].append((byDate[FAILURES] / byDate[TREATMENTS]))
                else:
                    values[key].append(byDate[LAYOUT[key][0]])
        
        for key in LAYOUT:
            values[key] = np.transpose(values[key])
            if len(results[key]) != 0:
                results[key] = np.vstack((results[key], values[key]))
            else:
                results[key] = values[key]

        count += 1
        if count == 5: break
        #progressBar(count, len(replicates))


    # Filter the list to those after the policy introduction
    temp = [startDate + datetime.timedelta(days=value) for value in dates]
    for ndx in range(len(temp)):
        if temp[ndx] < rwanda.POLICYDATE:
            dates[ndx] = 0
    dates = [value for value in dates if value != 0]

    return dates, results


def plot(dates, data, layout):

    # Parse the dates so that we just display the year number
    days = rwanda.POLICYDATE.date() - datetime.date(2003, 1, 1)
    dates = [(value - days.days) / 365 for value in dates]

    # Load the plotter and prepare the axes
    matplotlib.rc_file('matplotlibrc-line')
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Plot the axes data
    for filename in layout['sources']:
        for element in layout['left']:
            ax1.plot(dates, np.percentile(data[filename][element], 50, axis=0), label = layout['labels'][element])

        for element in layout['right']:
            ax2.plot(dates, np.percentile(data[filename][element], 50, axis=0), label = layout['labels'][element])

    # Format the plot
    ax1.legend()
    ax1.set_ylabel('% Treatment Failures / Genotype Frequency')

    ax2.legend(loc=0)
    ax2.set_ylabel('PfPR 2 to 10')
    ax2.set_xlim([dates[6], dates[-6]])
    ax2.set_title(layout['title'])

    plt.savefig('{}/{}.png'.format('plots/', layout['title']))


def formatPfPR(data):
    for key in data.keys():
        if not 'pfpr' in data[key].keys():
            return data

        # Apply a 12-month smoothing to the PfPR data
        pfpr = data[key]['pfpr']
        kernel = np.ones(12) / 12
        for ndx in range(len(pfpr)):
            pfpr[ndx] = np.convolve(pfpr[ndx], kernel, mode = 'same')

    return data


if __name__ == '__main__':
    al_vs_al5 = {
        'sources' : [ 
            '../Analysis/data/genotype_dataset/rwa-pfpr-constant.csv',
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv'
        ],

        'plots' : ['tf', 'pfpr', 'freq_561h'],
        'left' : ['tf', 'freq_561h'],
        'right' : ['pfpr'],

        'title' : 'AL 3-day vs. AL 5-day',
        'labels' : {
            'tf' : '% Treatment Failures',
            'pfpr' : 'PfPR 2 to 10',
            'freq_561h' : '561H Frequency'
        }
    }

    dates, data = load(al_vs_al5['sources'])
    data = formatPfPR(data)
    plot(dates, data, al_vs_al5)

