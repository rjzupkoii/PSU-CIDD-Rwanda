#!/usr/bin/env python3

# rwa_plot_genotype.py
#
# Generated the more complicated overlay plots for the key manuscript figures.
import csv
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

import rwanda

from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker

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
def generate(layout, cached=False):
    # Load and save the data if it wasn't cached
    if not cached:          
        dates, data = load(layout)
        if not os.path.exists('np'):
            os.makedirs('np')
        for key in data.keys():
            filename = 'np/{}'.format(key.split('/')[-1].replace('.csv', '-parsed.csv'))
            writeCsv(dates, data[key], filename)
        np.save('np/{}'.format(layout['title']), data, allow_pickle=True)
        np.save('np/rwa-dates', dates, allow_pickle=True)

    # Data was cached, load it
    else:
        print('Loading  {}...'.format(layout['title']))
        data = np.load('np/{}.npy'.format(layout['title']), allow_pickle=True)
        dates = np.load('np/rwa-dates.npy', allow_pickle=True)    
        data = dict(enumerate(data.flatten(), 0))[0]

    # Plot the data
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
                elif 'tf' == index:
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
        'pfpr' : '#cfcfcf',
        'freq_561h' : '#3182bd',

        # Note we use the same color for the next two
        'freq_plasmepsin' : '#bf6ffd',
        'freq_double' : '#bf6ffd'
    }
    
    # Generate all of the graphic elements for this axis
    def handle_axis(plot, axis):
        for element in plot:
            color = COLORS[element]
            style = iter(layout['style'])
            name = iter(layout['name'])
            for filename in layout['source']:
                smooth = True if element == 'pfpr' else False
                color = handle_data(axis, data[filename][element],  
                    '{}, {}'.format(layout['label'][element], next(name)), color, next(style), smooth)

    # Update the current plot with the median of the data and shaded IQR
    def handle_data(axis, data, label, color, style, smooth):
        upper = np.percentile(data, 75, axis=0)
        median = np.percentile(data, 50, axis=0)
        lower = np.percentile(data, 25, axis=0)

        if smooth: 
            upper = pd.Series(upper).rolling(12, min_periods=1).mean()
            median = pd.Series(median).rolling(12, min_periods=1).mean()
            lower = pd.Series(lower).rolling(12, min_periods=1).mean()

        line = axis.plot(dates, median, style, label = label, color = color, linewidth = 5)
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

    # Add the three color left y-axis label
    box = [
        TextArea('% Treatment Failures', textprops=dict(color='#c61815', rotation=90, ha='left', va='bottom')),
        TextArea(' / ', textprops=dict(color='black', rotation=90, ha='left', va='bottom')),
        TextArea(' '*16 + 'Genotype Frequency', textprops=dict(color='#3182bd', rotation=90, ha='left', va='bottom')),
    ]
    ybox = VPacker(children=box, align="bottom", pad=0, sep=5)
    anchored = AnchoredOffsetbox(loc='center', child=ybox, pad=0, frameon=False, bbox_to_anchor=(-0.08, 0.4), 
                                  bbox_transform=ax1.transAxes, borderpad=0)
    ax1.add_artist(anchored)    

    # Format the axes
    ax1.grid(False)
    ax1.set_ylim([0, 1])
    labels = ['{:.1f} / {:.0f}%'.format(tick, tick * 100) for tick in ax1.get_yticks()]
    ax1.set_yticks(ax1.get_yticks())        # Redundant, but keeps the formatter happy
    ax1.set_yticklabels(labels)

    ax2.grid(False)
    ax2.set_ylabel('$\it{Pf}$PR$_{2-10}$', color='#686868')
    ax2.set_ylim([0, 5.25])
    ax2.set_xlim([dates[12], dates[len(dates) - 1]])

    # Format the plot
    ax1.set_title(layout['title'])
    ax1.set_xlabel('Years Since Intervention')
  
    if not os.path.exists('plots'):
        os.makedirs('plots')
    filename = '{}/{}.png'.format('plots/', layout['title'])
    plt.savefig(filename)
    print('Saved, {}'.format(filename))

def writeCsv(dates, data, filename):
    # Start by writing out raw CSV
    with open(filename, 'w') as out:
        # Start by writing the dates
        values = ','.join([str(item) for item in dates])
        out.write("{},{}\n".format('date', values))    
    
        # Write the median and IQR for each keyed value
        for key in data.keys():
            for value in [25, 50, 75]:
                if key == 'pfpr':
                    values = ','.join([str(item) for item in pd.Series(np.percentile(data[key], value, axis=0)).rolling(12, min_periods=1).mean()  ])
                else:
                    values = ','.join([str(item) for item in np.percentile(data[key], value, axis=0)])
                out.write("{}-{},{}\n".format(key, value, values))

    # Transpose the CSV from horizontal to vertical alignment
    values = zip(*csv.reader(open(filename, "r")))
    csv.writer(open(filename, "w")).writerows(values)
        

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
        'intervention' : 0.42,

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
        'intervention' : 0.42,

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
        'intervention' : 0.42,

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
        'intervention' : 0.42,

        'title' : 'AL 5-day vs. DHA-PPQ - Double Resistance',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
            'freq_double' : 'Double Resistance Frequency'
        }        
    }      
    al5_vs_mft= {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-mft-asaq-dhappq-0.25.csv'
        ],
        'name' : ['AL 5-day', 'MFT' ],

        'plot' : ['tf', 'pfpr', 'freq_561h', 'freq_double'],
        'left' : ['tf', 'freq_561h', 'freq_double'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.42,

        'title' : 'AL 5-day vs. MFT (75% ASAQ, 25% DHA-PPQ)',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
            'freq_double' : 'Double Resistance Frequency'
        }        
    }      
    al5_vs_cycling = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-rotation-al-5.csv'
        ],
        'name' : ['AL 5-day', 'DHA-PPQ rotation to MFT' ],

        'plot' : ['tf', 'pfpr', 'freq_561h', 'freq_double'],
        'left' : ['tf', 'freq_561h', 'freq_double'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.40,

        'title' : 'AL 5-day vs. DHA-PPQ rotation to MFT',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
            'freq_double' : 'Double Resistance Frequency'
        }        
    }      
    al5_vs_tact = {
        'source' : [ 
            '../Analysis/data/genotype_dataset/rwa-ae-al-5.csv',
            '../Analysis/data/genotype_dataset/rwa-tact-alaq.csv'
        ],
        'name' : ['AL 5-day', 'AL + AQ' ],

        'plot' : ['tf', 'pfpr', 'freq_561h'],
        'left' : ['tf', 'freq_561h'],
        'right' : ['pfpr'],
        'style' : ['-.', '-'],
        'intervention' : 0.41,

        'title' : 'AL 5-day vs. AL + AQ',
        'label' : {
            'tf' : '% Treatment Failures',
            'pfpr' : '$\it{Pf}$PR$_{2-10}$',
            'freq_561h' : '561H Frequency',
        }        
    }                  

    # NOTE Things will crash if this is set to True and the files are not present
    cached = False
    generate(al_vs_al5, cached)
    generate(al5_vs_dhappq, cached)
    generate(al5_vs_dhappq_plas, cached)    
    generate(al5_vs_dhappq_double, cached)
    generate(al5_vs_mft, cached)
    generate(al5_vs_cycling, cached)
    generate(al5_vs_tact, cached)
