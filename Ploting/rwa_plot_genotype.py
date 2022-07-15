#!/usr/bin/env python3

# rwa_plot_genotype.py
#
# Generated the more complicated overlay plots for the key manuscript figures.
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

# Date to start plotting from
PLOTDATE = datetime.datetime(2020, 1, 1)

INDICES = {
    'replicate' : 0,
    'dates' : 1,
    'infections' : 3,
    'treatments' : 5,
    'failures' : 6,
    'pfpr' : 7,
    'freq_561h' : 10,
    'freq_plasmepsin' : 13,
    'freq_double' : 16
}

# Generate the plot using the layout provided
def generate(layout):
    dates, data = load(layout)
    data = formatPfPR(data)
    plot(dates, data, layout)


# Load all of the files that have been provided
def load(layout):
    results = {}
    for filename in layout['source']:
        dates, result = parse(filename, layout['plot'])
        results[filename] = result
    return dates, results

# Load a single file that contains genotype data
def parse(filename, plots):
    # Load the data and parse out the common data
    data = pd.read_csv(filename, header = None)
    dates = data[INDICES['dates']].unique().tolist()
    replicates = data[INDICES['replicate']].unique().tolist()

    # Note the project state date
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")

    # Prepare the results data structure
    results = {}
    for index in plots: results[index] = []

    # Iterate over each of the replicates
    count = 0
    for replicate in replicates:
        byReplicate = data[data[INDICES['replicate']] == replicate]

        # Prepare the data structure for this replicate
        values = {}
        for index in plots: values[index] = []

        for date in dates:
            # Continue if we haven't got to the intervention date 
            currentDate = startDate + datetime.timedelta(days=date)
            if currentDate < PLOTDATE: continue

            # Append the data for this date
            byDate = byReplicate[byReplicate[INDICES['dates']] == date]
            for index in plots:
                if 'freq_' in index:
                    values[index].append(byDate[INDICES[index]] / byDate[INDICES['infections']])
                elif 'tf' is index:
                    values[index].append((byDate[INDICES['failures']] / byDate[INDICES['treatments']]))
                else:
                    values[index].append(byDate[INDICES[index]])
        
        for index in plots:
            values[index] = np.transpose(values[index])
            if len(results[index]) != 0:
                results[index] = np.vstack((results[index], values[index]))
            else:
                results[index] = values[index]

        count += 1
        progressBar(count, len(replicates))

    # Filter the list to those after the plot date
    temp = [startDate + datetime.timedelta(days=value) for value in dates]
    for ndx in range(len(temp)):
        if temp[ndx] < PLOTDATE: dates[ndx] = 0
    dates = [value for value in dates if value != 0]

    # Return the filtered dates and processed results
    return dates, results


# Plot using Matplotlib
def plot(dates, data, layout):       
    COLORS = {
        'tf' : '#fb9a99',
        'pfpr' : '#a6cee3',
        'freq_561h' : '#fdbf6f',

        # Note we use the same color for the next two
        'freq_plasmepsin' : '#67503d',
        'freq_double' : '#67503d'
    }
    
    # Generate all of the graphic elements for this axis
    def handle_axis(plot, axis):
        for element in plot:
            color = COLORS[element]
            style = iter(layout['style'])
            name = iter(layout['name'])
            for filename in layout['source']:
                color = handle_data(axis, data[filename][element], '{}, {}'.format(layout['label'][element], next(name)), color, next(style))

    # Update the current plot with the median of the data and shaded IQR
    def handle_data(axis, data, label, color, style):
        upper = np.percentile(data, 75, axis=0)
        median = np.percentile(data, 50, axis=0)
        lower = np.percentile(data, 25, axis=0)
        line = axis.plot(dates, median, style, label = label, color = color, linewidth = 3)
        fill = scale_luminosity(line[0].get_color(), 1)
        axis.fill_between(dates, lower, upper, alpha=0.5, facecolor=fill)
        return scale_luminosity(color, 0.5)

    # Parse the dates so that we just display the year number
    days = rwanda.POLICYDATE.date() - datetime.date(2003, 1, 1)
    dates = [(value - days.days) / 365 for value in dates]

    # Load the plotter and prepare the axes
    matplotlib.rc_file('matplotlibrc-line')
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()   

    # Plot the axes data
    handle_axis(layout['left'], ax1)
    handle_axis(layout['right'], ax2)

    # Plot the intervention point
    plt.axvline(0, color='#a5a5a5')
    ax1.text(-0.175, layout['intervention'], 'Drug Policy Introduction', rotation=90, size=20, color='#a5a5a5')

    # Format the legend
    fig.legend(loc='lower center', ncol=len(layout['plot']), borderpad=0.25, frameon=False, prop={'size': 20})

    # Format the axes
    ax1.grid(False)
    ax1.set_ylabel('Genotype Frequency / % Treatment Failures')
    ax1.set_ylim([0, 1])
    labels = ['{:.1f} / {:.0f}%'.format(tick, tick * 100) for tick in ax1.get_yticks()]
    ax1.set_yticks(ax1.get_yticks())        # Redundant, but keeps the formatter happy
    ax1.set_yticklabels(labels)

    ax2.grid(False)
    ax2.set_ylabel('$\it{Pf}$PR$_{2-10}$')
    ax2.set_xlim([dates[6], dates[-6]])

    # Format the plot
    ax1.set_title(layout['title'])
    ax1.set_xlabel('Years Since Intervention')
  
    filename = '{}/{}.png'.format('plots/', layout['title'])
    plt.savefig(filename)
    print('Saved, {}'.format(filename))


# Apply a 12-month smoothing to the PfPR data
def formatPfPR(data):
    kernel = np.ones(12) / 12
    for index in data.keys():
        if not 'pfpr' in data[index].keys(): return data
        pfpr = data[index]['pfpr']
        for ndx in range(len(pfpr)):
            pfpr[ndx] = np.convolve(pfpr[ndx], kernel, mode = 'same')
    return data


if __name__ == '__main__':
    al_vs_al5 = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-pfpr-constant.csv',
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv'
        ],
        'name' : ['AL 3-day', 'AL 5-day'],

        'plot' : ['tf', 'pfpr', 'freq_561h'],
        'left' : ['tf', 'freq_561h'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.45,

        'title' : 'AL 3-day vs. AL 5-day',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency'
        }
    }
    al5_vs_dhappq = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-replacement-dhappq.csv'
        ],
        'name' : ['AL 5-day', 'DHA-PPQ' ],

        'plot' : ['tf', 'pfpr', 'freq_561h'],
        'left' : ['tf', 'freq_561h'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.65,

        'title' : 'AL 5-day vs. DHA-PPQ',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
        }        
    }
    al5_vs_dhappq_plas = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-replacement-dhappq.csv'
        ],
        'name' : ['AL 5-day', 'DHA-PPQ' ],

        'plot' : ['tf', 'pfpr', 'freq_561h', 'freq_plasmepsin'],
        'left' : ['tf', 'freq_561h', 'freq_plasmepsin'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.65,

        'title' : 'AL 5-day vs. DHA-PPQ - Plasmepsin 2-3, 2x Copy',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
            'freq_plasmepsin' : 'Plasmepsin 2-3, 2x copy Frequency'
        }        
    }    
    al5_vs_dhappq_double = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-replacement-dhappq.csv'
        ],
        'name' : ['AL 5-day', 'DHA-PPQ' ],

        'plot' : ['tf', 'pfpr', 'freq_561h', 'freq_double'],
        'left' : ['tf', 'freq_561h', 'freq_double'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.65,

        'title' : 'AL 5-day vs. DHA-PPQ - Double Resistance',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
            'freq_double' : 'Double Resistance Frequency'
        }        
    }      

    generate(al_vs_al5)
    generate(al5_vs_dhappq)
    generate(al5_vs_dhappq_plas)
    generate(al5_vs_dhappq_double)
