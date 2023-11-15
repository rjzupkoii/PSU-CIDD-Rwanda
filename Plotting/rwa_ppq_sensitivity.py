#!/usr/bin/env python3

# rwa_ppq_sensitivity.py
#
# Generate extended / supplemental figures concerning the piperaquine (PPQ) 
# sensitvity to mutation rate and EC50.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

import rwanda

sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
from utility import progressBar

PATH = '../Analysis/data/datasets/{}'


def load(filename):
    REPLICATE, DATES, TREATMENTS, FAILURES = 1, 2, 9, 10

    # Load the data, note the unique dates, replicates
    data = pd.read_csv(filename, header = None)
    dates = data[DATES].unique().tolist()
    replicates = data[REPLICATE].unique().tolist()

    # Load the treatment failures from the data set
    count, failures = 0, []
    for replicate in replicates:
        byReplicate = data[data[REPLICATE] == replicate]
        temp = []
        for date in dates:
            byDate = byReplicate[byReplicate[DATES] == date]
            temp.append((sum(byDate[FAILURES]) / sum(byDate[TREATMENTS])) * 100.0)
        if len(failures) != 0: failures = np.vstack((failures, temp))
        else: failures = temp

        # Update the progress bar
        count += 1
        progressBar(count, len(replicates))

    # Return the results
    return dates, failures    


def plot_data(data, dates, ax):
    # Find the bounds of the data
    upper = np.percentile(data, 75, axis=0)
    median = np.percentile(data, 50, axis=0)
    lower = np.percentile(data, 25, axis=0)

    # Add the data to the subplot
    ax.plot(dates, median)
    color = scale_luminosity(ax.lines[-1].get_color(), 1)
    ax.fill_between(dates, lower, upper, alpha=0.5, facecolor=color)
    return ax, np.nanmax(upper)


def sensitivity_mutation_figure(rows, cols, layout, title, filename):
    # Prepare the figure
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(rows, cols)
    
    for item in layout:
        # Check to see if the plot is not visible
        row = item[0]; col = item[1]
        if item[2] is None:
            axes[row, col].set_visible(False)
            continue        
        
        # Load the data and format the dates
        dates, frequencies = rwanda.prepare_validation(PATH.format(item[2]))
        startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
        dates = [startDate + datetime.timedelta(days=x) for x in dates]
        
        # Add the data to the plot
        axes[row, col], limit = plot_data(frequencies, dates, axes[row, col])
        axes[row, col].title.set_text(item[3])
        
        # Add the intervention line
        plt.sca(axes[row, col])
        plt.axvline(x = datetime.datetime(2024, 1, 1), linestyle = ':', color = 'gray')
        
        # Format the axis
        axes[row, col].set_ylim([0.35, 1])
        axes[row, col].set_xlim([datetime.datetime(2023, 1, 1), max(dates)])
        if col == 0: plt.ylabel('561H Frequency')
        
    # Set the main title
    fig = plt.gcf()
    fig.suptitle(title)

    # Save the plot
    plt.savefig(filename, dpi = 300)
    plt.close()
       
    
def sensitivity_treatment_figure(rows, cols, layout, title, filename):
    # Prepare the figure
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(rows, cols)

    for item in layout:
        # Check to see if the plot is not visible
        row = item[0]; col = item[1]
        if item[2] is None:
            axes[row, col].set_visible(False)
            continue
        
        # Load the data and format the dates
        dates, data = load(PATH.format(item[2]))
        startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
        dates = [startDate + datetime.timedelta(days=x) for x in dates]
        
        # Add the data to the plot
        axes[row, col], limit = plot_data(data, dates, axes[row, col])
        axes[row, col].title.set_text(item[3])
                
        # Format the axis
        axes[row, col].set_ylim([0, 100])
        axes[row, col].set_xlim([datetime.datetime(2024, 1, 1), max(dates)])
        if col == 0: 
            plt.sca(axes[row, col])
            plt.ylabel('Percent Treatment Failures')
                        
    # Set the main title
    fig = plt.gcf()
    fig.suptitle(title)
            
    # Save the plot
    plt.savefig(filename, dpi = 300)
    plt.close()            
    

if __name__ == '__main__':
    layout = [
        [0, 0, 'rwa-dhappq-0.25.csv', '0.25x Mutation Rate'],
        [1, 0, 'rwa-dhappq-0.5.csv', '0.5x Mutation Rate'],
        
        [0, 1, 'rwa-replacement-dhappq.csv', 'Calibrated Mutation Rate'],
        [1, 1, None, None],
        
        [0, 2, 'rwa-dhappq-1.25.csv', '1.25x Mutation Rate'],
        [1, 2, 'rwa-dhappq-1.5.csv', '1.5x Mutation Rate'],
    ]
    sensitivity_mutation_figure(2, 3, layout, 
        'Sensitivity of 561H frequency to Plasmepsin 2/3 mutation rate', 
        'plots/rwa-ppq-frequency-sensitivity.png')
    sensitivity_treatment_figure(2, 3, layout, 
        'Sensitivity of treatment failures to Plasmepsin 2/3 mutation rate', 
        'plots/rwa-ppq-failures-sensitivity.png')
    
    layout = [
        [0, 0, 'rwa-dhappq-ec50-1.0.csv', 'EC50 = 1.0'],
        [0, 1, 'rwa-dhappq-ec50-1.1.csv', 'EC50 = 1.1'],
        [0, 2, 'rwa-dhappq-ec50-1.2.csv', 'EC50 = 1.2'],
        [0, 3, 'rwa-dhappq-ec50-1.3.csv', 'EC50 = 1.3'],
        [1, 0, 'rwa-replacement-dhappq.csv', 'EC50 = 1.4 (Calibrated)'],
        [1, 1, 'rwa-dhappq-ec50-1.5.csv', 'EC50 = 1.5'],
        [1, 2, 'rwa-dhappq-ec50-1.6.csv', 'EC50 = 1.6'],
        [1, 3, None, None]
    ]
    sensitivity_mutation_figure(2, 4, layout, 
        'Sensitivity of 561H frequency to PPQ EC50', 
        'plots/rwa-ppq-frequency-ec50.png')
    sensitivity_treatment_figure(2, 4, layout, 
        'Sensitivity of treatment failures to PPQ EC50', 
        'plots/rwa-ppq-failures-ec50.png')