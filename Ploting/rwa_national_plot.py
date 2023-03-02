#!/usr/bin/env python3

# rwa_561H_plot.py
#
# Plot the 561H validation replicates, within spiking studies labeled.
import argparse
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
import rwa_reports

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from utility import progressBar


def main(plot, year, verification, search, summary=False, breaks=[3, 5, None]):
    # Make sure a plots directory is present
    if not os.path.exists('plots'):
        os.makedirs('plots')

    # Note the policy date
    policy_date = datetime.datetime(year, 1, 1)

    if verification:
        print('Parsing 561H verification data ...')
        os.makedirs('plots', exist_ok=True)
        filename = os.path.join(rwanda.DATA_PATH.format(year), 'rwa-pfpr-constant.csv')
        rwanda.plot_validation(filename, 'plots/{} - 561H Verification.png'.format(year))

    for years in breaks:
        dataset = {}
        for filename in rwanda.CONFIGURATIONS:
            # Speed things up by only parsing the data we need
            if search == 'standard' and not any (filter in filename for filter in ['constant', 'ae-al', 'replacement', 'mft', 'rotation']):
                continue
            elif search == 'compliance' and not any(filter in filename for filter in ['high', 'moderate', 'low']):
                continue
            elif search == 'dhappq' and not any(filter in filename for filter in ['dhappq', 'constant']):
                continue
            elif search == 'experimental' and not any(filter in filename for filter in ['constant', '3-4-3', 'seq', 'tact']):
                continue
            elif search == 'nmcp' and not any(filter in filename for filter in ['-nmcp', 'constant']):
                continue

            # Pass if the file does not exist, this should only happen if we are actively running replicates
            if not os.path.exists(os.path.join(rwanda.DATA_PATH.format(year), filename)):
                print('Skipping {} ...'.format(filename))
                continue

            # Load the data, apply the relevant filter
            print('Parsing {} ...'.format(filename))
            filter, prefix = None, ''
            if years is not None:
                filter = policy_date + relativedelta(years=years)
                prefix = "{} - ".format(years)
            results = prepare_national(os.path.join(rwanda.DATA_PATH.format(year), filename), year, filter=filter)

            # Plot the summary figure
            if summary: rwanda.plot_summary(rwanda.CONFIGURATIONS[filename], *results, prefix=prefix)   
            dataset[filename] = results[1]

        EXTENSION = 'png'
        for key in rwanda.REPORT_LAYOUT:
            label = rwanda.REPORT_LAYOUT[key][rwanda.REPORT_YLABEL]
            filename = 'plots/{} - {}.{}'.format(search.capitalize(), label, EXTENSION)
            if years is not None:
                filename = 'plots/{} - {:02d}y - {}.{}'.format(search.capitalize(), years, label, EXTENSION)
            plot_violin(dataset, key, label, filename, plot)
            print("Created {}...".format(filename))


def plot_violin(dataset, filter, label, imagefile, plot):
    LABEL, COLOR = range(2)

    # If the filter is for treatments, then return since it's just a sentinel
    if filter == 'treatments':
        return

    # Parse the last entry in the data for the violin plot
    data, labels, colors, prefix = [], [], [], ''
    for key in plot:
        # Filter to the data we want
        if key not in dataset: 
            continue
        temp = np.matrix(dataset[key][filter])

        # If the filter is for frequency then just reshape
        if filter == 'frequency':
            temp = np.asarray(temp[:, -1].T).reshape(-1) 

        # Treatment failures need to be reported as a percentage of treatments
        elif filter == 'failures':
            treatments = np.matrix(dataset[key]['treatments'])
            failures = np.matrix(dataset[key]['failures'])
            temp = (np.sum(failures[:, -12:], axis=1) / np.sum(treatments[:, -12:], axis=1)) * 100.0
            temp = np.asarray(temp).reshape(-1)
            prefix = 'Percent'

        # Otherwise we want the monthly average of the last 12 months
        else:
            temp = np.sum(temp[:, -12:], axis=1) / 12
            temp = np.asarray(temp).reshape(-1)
            prefix = 'Monthly'
 
        # Append to the working data and update the labels            
        data.append(temp)
        labels.append(plot[key][LABEL])
        colors.append(plot[key][COLOR])

    # Generate the plot
    matplotlib.rc_file("matplotlibrc-violin")
    figure, axis = plt.subplots()
    violin = sb.violinplot(data=data, palette=colors, cut=0, scale='width', inner=None, linewidth=0.5, orient='h')   
    sb.boxplot(data=data, palette=colors, width=0.2, boxprops={'zorder' : 2}, orient='h')
    sb.despine(top=True, right=True, left=True, bottom=True)

    # Scale the alpha channel for the violin plot
    for item in violin.collections: item.set_alpha(0.5)

    # Format the plot for the data
    axis.set_yticklabels(labels)
    axis.set_xlabel("{} {}".format(prefix, label))   
    if prefix != '':
        axis.xaxis.set_major_formatter(ticker.EngFormatter())
    
    # Finalize the image as proof (png) or print (tif)
    if imagefile.endswith('svg'):
        plt.savefig(imagefile, dpi=1200, format="svg")
    elif imagefile.endswith('tif'):
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    else:
        plt.savefig(imagefile)
    plt.close()
        

def prepare_national(filename, year, filter=None):
    REPLICATE, DATES, DISTRICT, INDIVIDUALS, WEIGHTED = 1, 2, 3, 4, 8

    # Load the data, note the unique dates, replicates
    policy_date = datetime.datetime(year, 1, 1)
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
                if currentDate < policy_date: continue
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
            if currentDate == policy_date: 
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

if __name__ == '__main__':
    # Parse the arguments
    plots_list = ', '.join(rwa_reports.PLOTS.keys())
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', dest='verification', help='Plot the verification data')
    parser.add_argument('-y', action='store', dest='year', required=True, help='Year filter for the studies')
    parser.add_argument('-p', action='store', dest='plot', default='standard', 
                        help='The plot to generate, must one of: {}. Default: standard'.format(plots_list))
    args = parser.parse_args()

    # Check the inputs
    plot = args.plot.lower()
    if plot not in rwa_reports.PLOTS.keys():
        sys.stderr.write('The plot {} does not appear in the list of plots ({}).\n'.format(args.plot, plots_list))
        sys.exit(1)
    
    # Plot the more experimental protocols
    main(rwa_reports.PLOTS[args.plot.lower()], int(args.year), args.verification, plot)

    