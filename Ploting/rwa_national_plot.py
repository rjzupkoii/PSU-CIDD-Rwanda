#!/usr/bin/env python3

# rwa_561H_plot.py
#
# Plot the 561H validation replicates, within spiking studies labeled.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd
import seaborn as sb
import sys

from dateutil.relativedelta import relativedelta

import rwanda

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
from utility import progressBar


def main(nmcp=False):
    print('Parsing 561H verification data ...')
    os.makedirs('plots', exist_ok=True)
    filename = os.path.join(rwanda.DATA_PATH, 'rwa-561h-verification.csv')
    plot_validation(filename, 'plots/561H Verification.png')
    filename = os.path.join(rwanda.DATA_PATH, 'rwa-spike.csv')
    plot_validation(filename, 'plots/561H Spikes.png')

    for years in [3, 5, None]:
        dataset = {}
        for filename in rwanda.CONFIGURATIONS:
            # Press on if we are not dealing with NMCP scenarios
            if not nmcp and '-nmcp-' in filename:
                continue
            if nmcp and not ('-constant' in filename or '-nmcp-' in filename):
                continue

            # Load the data, apply the relevent filter
            print('Parsing {} ...'.format(filename))
            filter, prefix = None, ''
            if years is not None:
                filter = rwanda.POLICYDATE + relativedelta(years=years)
                prefix = "{} - ".format(years)
            results = prepare_national(os.path.join(rwanda.DATA_PATH, filename), filter=filter)

            # Plot the summary figure
            rwanda.plot_summary(rwanda.CONFIGURATIONS[filename], *results, prefix=prefix)   
            dataset[filename] = results[1]

        for key in rwanda.REPORT_LAYOUT:
            ylabel = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_YLABEL]
            filename = 'plots/Comparison - {}.png'.format(ylabel)
            if years is not None:
                filename = 'plots/Comparison, {}y - {}.png'.format(years, ylabel)
            plot_violin(dataset, key, ylabel, filename, nmcp)      


def plot_violin(dataset, filter, ylabel, imagefile, nmcp):
    LABEL, COLOR = range(2)
    ORDER = {
        # Status Quo
        'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

        # Extend AL
        'rwa-ae-al-4.csv'              : ['AL, 4 days', '#bdd7e7'],
        'rwa-ae-al-5.csv'              : ['AL, 5 days', '#bdd7e7'],

        # Replace AL
        'rwa-replacement-asaq.csv'     : ['100% ASAQ', '#6baed6'],
        'rwa-replacement-dhappq.csv'   : ['100% DHA-PPQ', '#6baed6'],

        # AL / ASAQ MFT
        'rwa-mft-al-asaq-0.25.csv'     : ['AL (75%) + ASAQ (25%)', '#bae4b3'],
        'rwa-mft-al-asaq.csv'          : ['AL (50%) + ASAQ (50%)', '#bae4b3'],
        'rwa-mft-al-asaq-0.75.csv'     : ['AL (25%) + ASAQ (75%)', '#bae4b3'],

        # AL / DHA-PPQ MFT
        'rwa-mft-al-dhappq-0.25.csv'   : ['AL (75%) + DHA-PPQ (25%)', '#74c476'],
        'rwa-mft-al-dhappq.csv'        : ['AL (50%) + DHA-PPQ (50%)', '#74c476'],
        'rwa-mft-al-dhappq-0.75.csv'   : ['AL (25%) + DHA-PPQ (75%)', '#74c476'],

        # ASAQ / DHA-PPQ MFT
        'rwa-mft-asaq-dhappq-0.25.csv' : ['ASAQ (75%) + DHA-PPQ (25%)', '#31a354'],
        'rwa-mft-asaq-dhappq.csv'      : ['ASAQ (50%) + DHA-PPQ (50%)', '#31a354'],
        'rwa-mft-asaq-dhappq-0.75.csv' : ['ASAQ (25%) + DHA-PPQ (75%)', '#31a354'],

        # Rotate DHA-PPQ
        'rwa-rotation-al-3.csv'        : ['DHA-PPQ (3 years) / AL (50%) + ASAQ', '#d7b5d8'],
        'rwa-rotation-al-5.csv'        : ['DHA-PPQ (3 years) / AL, 5 days (50%) + ASAQ', '#d7b5d8'],

        # TACT
        'rwa-tact-alaq.csv'            : ['AL + AQ', '#df65b0'],
        'rwa-tact-dhappqmq.csv'        : ['DHA-PPQ + MQ', '#df65b0'],
    }

    # NMCP scenarios
    NMCP = {
        # Status Quo
        'rwa-pfpr-constant.csv' : ['Status Quo', '#88CCEE'],

        # Scenario 1, MFT AL (5-day) and DHA-PPQ
        'rwa-nmcp-1a.csv'       : ['1a', '#44AA99'],
        'rwa-nmcp-1b.csv'       : ['1b', '#44AA99'],
        'rwa-nmcp-1c.csv'       : ['1c', '#44AA99'],

        # Scenario 2, sensitivity analysis for scenario 1a
        'rwa-nmcp-2a.csv'       : ['2a', '#117733'],

        # Scenario 3c, MFT AL (5-day), DHA-PPQ, and ASAQ / Prolonged ASAQ adoption
        'rwa-nmcp-3c.csv'       : ['3c', '#DDCC77'],

        # Scenario 4c, MFT AL (5-day), DHA-PPQ, and ASAQ / Rapid ASAQ adoption
        'rwa-nmcp-4c.csv'       : ['4c', '#A691AE'],
    }

    # Variable with the dataset to use for the studies
    plot = ORDER
    if nmcp:
        plot = NMCP

    # Parse the last entry in the data for the violin plot
    data, labels, colors, prefix = [], [], [], ''
    for key in plot:
        # Filter to the data we want
        temp = np.matrix(dataset[key][filter])

        # If it's not frequency we want the monthly average of the last 12 months
        if filter != 'frequency':
            temp = np.sum(temp[:, -12:], axis=1) / 12
            temp = np.asarray(temp).reshape(-1)
            prefix = 'Total '
        else:
            temp = np.asarray(temp[:, -1].T).reshape(-1)  

        # Append to the working data and update the labels            
        data.append(temp)
        labels.append(plot[key][LABEL])
        colors.append(plot[key][COLOR])

    # Generate the plot
    matplotlib.rc_file("matplotlibrc-violin")
    figure, axis = plt.subplots()
    violin = sb.violinplot(data=data, palette=colors, cut=0, scale='width', inner=None, linewidth=0.5)   
    sb.boxplot(data=data, palette=colors, width=0.2, boxprops={'zorder' : 2})
    sb.despine(top=True, right=True, left=True, bottom=True)

    # Scale the alpha channel for the violin plot
    for item in violin.collections: item.set_alpha(0.5)

    # Format the plot for the data
    axis.set_xticks(range(len(labels)))
    axis.set_xticklabels(labels)
    axis.tick_params(axis='x', rotation=30)
    plt.setp(axis.xaxis.get_majorticklabels(), ha='right')
    axis.set_ylabel(ylabel)
    if prefix != '':
        axis.yaxis.set_major_formatter(ticker.EngFormatter())
    
    # Finalize the image as proof (png) or print (tif)
    if imagefile.endswith('svg'):
        plt.savefig(imagefile, dpi=1200, format="svg")
    elif imagefile.endswith('tif'):
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    else:
        plt.savefig(imagefile)
        

def prepare_national(filename, filter=None):
    REPLICATE, DATES, DISTRICT, INDIVIDUALS, WEIGHTED = 1, 2, 3, 4, 8

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")

    # Build the dictionary for the results
    results = {}
    for key in rwanda.REPORT_LAYOUT:
        results[key] = []

    # Start by filtering by the replicate
    count, failed = 0, 0
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]

        # Prepare the data structure for this replicate
        values = {}
        for key in rwanda.REPORT_LAYOUT:
            values[key] = []

        # Next, filter by date so we can properly aggregate
        rejected = False
        for date in dates:    
            # Stop if this replicate was rejected
            if rejected: break

            # Verify the frequency if this is the correct date
            currentDate = startDate + datetime.timedelta(days=date)
            byDate = byReplicate[byReplicate[DATES] == date]
            if currentDate == rwanda.REFERENCEDATE:
                temp = byDate[byDate[DISTRICT] == rwanda.REFERENCEDISTRICT]
                if (temp[WEIGHTED] / temp[INDIVIDUALS]).values[0] < rwanda.REFERENCEFREQUENCY:
                    print((temp[WEIGHTED] / temp[INDIVIDUALS]).values[0])
                    failed += 1
                    rejected = True
                    continue            

            # If we are filtering then check the date
            if filter is not None:
                if currentDate < rwanda.POLICYDATE: continue
                if currentDate > filter: break

            # Store the appropriate data
            for key in rwanda.REPORT_LAYOUT:
                if key != 'frequency':
                    index = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_INDEX]
                    values[key].append(sum(byDate[index]))
                else:
                    values[key].append(sum(byDate[WEIGHTED]) / sum(byDate[INDIVIDUALS]))

        # Update the progress bar
        count += 1
        progressBar(count, len(replicates))

        # Add the data if not rejected
        if rejected: continue        
        for key in rwanda.REPORT_LAYOUT:
            if len(results[key]) != 0:
                results[key] = np.vstack((results[key], values[key]))
            else:
                results[key] = values[key]

    # Return the results
    if failed > 0: print('{} replicate(s) rejected'.format(failed))

    # Select the subset of dates if a filter was applied
    if filter is not None:
        start, end = 0, 0
        for ndx in range(len(dates)):
            currentDate = startDate + datetime.timedelta(days=dates[ndx])
            if currentDate == rwanda.POLICYDATE: 
                start = ndx
            if currentDate == filter:
                end = ndx
                break
        dates = dates[start:end + 1]

    # Return the results and dates
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
    main(True)