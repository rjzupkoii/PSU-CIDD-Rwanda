#!/usr/bin/env python3

# rwa_ext_fig_9.py
#
# Generate extended figure nine for the manuscript.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re
import sys

import rwanda

sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity

PATH = '../Analysis/ms_data/{}'
PLOTS =  [['2024/datasets/rwa-pfpr-constant.csv', 'sensitivity/rwa-fitness-10x.csv'],
          ['sensitivity/rwa-fitness-25x.csv', 'sensitivity/rwa-fitness-50x.csv']]
TITLES = [['Calibrated Fitness Cost', '10x Fitness Cost'],
          ['25x Fitness Cost', '50x Fitness Cost']]

def add_spikes(plot):
    DHS_DATA = np.array([
        # Kirby et al. 2022
        [4, 'Kirehe (0.056)', datetime.datetime(2015,9,30), 0.05556],
        [5, 'Ngoma (0.019)', datetime.datetime(2015,9,30), 0.01923],
    ])
    data_points = np.append(rwanda.SPIKES, DHS_DATA, axis=0)
    
    # Add the 561H data points
    for spikeId, label, x, y in data_points:           
        plot.scatter(x, y, color='black', s=50)
        match = re.search('(\d\.\d*)', label)
        plot.annotate(round(float(match.group(0)), 2), (x, y), 
                      textcoords='offset points', xytext=(0,10), 
                      ha='center', fontsize=18)


def plot_data(data, dates, ax):
    # Find the bounds of the data
    upper = np.percentile(data, 97.5, axis=0)
    median = np.percentile(data, 50, axis=0)
    lower = np.percentile(data, 2.5, axis=0)

    # Add the data to the subplot
    ax.plot(dates, median)
    color = scale_luminosity(ax.lines[-1].get_color(), 1)
    ax.fill_between(dates, lower, upper, alpha=0.5, facecolor=color)
    return ax, np.nanmax(upper)


def plot():
    # Prepare the figure
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(2, 2)
    
    # Parse the data and add it to the plot
    for row in range(len(PLOTS)):
        for col in range(len(PLOTS[row])):
            # Load the data
            dates, frequencies = rwanda.prepare_validation(PATH.format(PLOTS[row][col]))
            
            # Format the dates
            startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
            dates = [startDate + datetime.timedelta(days=x) for x in dates]
    
            # Add the data to the plot
            axes[row, col], limit = plot_data(frequencies, dates, axes[row, col])
            axes[row, col].title.set_text(TITLES[row][col])
            
            # Add the spikes to the plot
            plt.sca(axes[row, col])
            add_spikes(plt)
            
            # Format the axis
            axes[row, col].set_ylim([0, 1])
            axes[row, col].set_xlim([datetime.datetime(2014, 1, 1), max(dates)])
            if col == 0: plt.ylabel('561H Frequency')
    
    # Save the plot as SVG for additional processing
    plt.savefig('plots/Ext. Fig. 9.svg', dpi=1200, format="svg")
            

if __name__ == '__main__':
    plot()
