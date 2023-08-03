#!/usr/bin/env python3

# rwa_cycling.py
#
# Produce a basic plot of 561H frequency based upon the cycling time frames.
#
# Abbreviations: number of treatment failures (NTF)
import argparse
import datetime
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

import rwanda

sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity
from utility import progressBar


def box_plot(path, plot_type, offset = 0):
  
  # Prepare the figure
  matplotlib.rc_file('matplotlibrc-line')
  figure, axes = plt.subplots(2, 3)
  
  # Prepare the common values, or error if the plot isn't known
  startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
  if plot_type == 'failures':
    ylabel = 'Percent Treatment Failures'
    ylim = [0, 0.6]
  elif plot_type == 'ntf':
    ylabel = 'Number Treatment Failures'
    ylim = [0, 25000]
  else:
    sys.exit('Unknown box plot type, {}'.format(plot_type))
  
  row, col = 0, 0
  for days in [90, 180, 270, 365, 545, 730]:
    dates, replicates = load('../Analysis/data/{}/rwa-cycling-{}.csv'.format(path, days), plot_type)
    dates = [startDate + datetime.timedelta(days=x) for x in dates]
    
    # Parse the data into something the box plot can work with
    data, years, start = [], [], offset
    for end in range(12 + offset, len(dates), 12):
      data.append(np.mean(replicates[: , start:end], axis=1))
      years.append("'" + str(dates[end].year)[2:])
      start = end
    
    # Add the data to the plot along with any formatting
    axes[row, col].boxplot(data)
    axes[row, col].set_xticklabels(years)
    axes[row, col].title.set_text('{} days'.format(days))
    axes[row, col].set_ylim(ylim)
    if col == 0: 
      plt.sca(axes[row, col])
      plt.ylabel(ylabel)
    
    # Only show every other tick label
    for label in axes[row, col].xaxis.get_ticklabels()[1::2]:
      label.set_visible(False)
    
    # Move to the next subplot
    row, col = increment(row, col)
    
  # Set the main title and save the plot
  fig = plt.gcf()
  fig.suptitle('DHA-PPQ then AL Cycling')
  plt.savefig('plots/box_{}.png'.format(plot_type))
  plt.close()
  

def increment(row, col):
  col += 1
  if col % 3 == 0:
    row += 1
    col = 0
  return row, col


def load(filename, plot_type):
  if plot_type in ['frequency', 'failures', 'ntf']:
    REPLICATE, DATES, INFECTIONS, WEIGHTED, TREATMENTS, TREATMENT_FAILURES = 1, 2, 4, 8, 9, 10
  elif plot_type in ['double', 'pfpr', 'ppq']:
    REPLICATE, DATES, PFPR, INFECTIONS, WEIGHTED, DOUBLE_WEIGHTED = 0, 1, 7, 3, 13, 16
  
  # Load the data, calculate the frequency; note the unique dates, replicates
  data = pd.read_csv(filename, header = None)
  dates = data[DATES].unique().tolist()
  replicates = data[REPLICATE].unique().tolist()
  
  # Load the frequency from the data set
  count, plot_data = 0, []
  for replicate in replicates:
    byReplicate = data[data[REPLICATE] == replicate]
    
    # Genotype data is already aggregated nationally
    if plot_type == 'pfpr': temp = byReplicate[PFPR]
    elif plot_type == 'ppq': temp = byReplicate[WEIGHTED] / byReplicate[INFECTIONS]
    elif plot_type == 'double': temp = byReplicate[DOUBLE_WEIGHTED] / byReplicate[INFECTIONS]
    
    # Otherwise the district data needs to be aggregated
    else:
      temp = []
      for date in dates:
        byDate = byReplicate[byReplicate[DATES] == date]
        if plot_type == 'frequency': temp.append(sum(byDate[WEIGHTED]) / sum(byDate[INFECTIONS]))
        elif plot_type == 'failures': temp.append(sum(byDate[TREATMENT_FAILURES]) / sum(byDate[TREATMENTS]))
        elif plot_type == 'ntf': temp.append(sum(byDate[TREATMENT_FAILURES]))
    
    # Update the data to be returned
    if len(plot_data) != 0: plot_data = np.vstack((plot_data, temp))
    else: plot_data = temp
  
    # Update the progress bar
    count += 1
    progressBar(count, len(replicates))
  
  # Return the results
  return dates, plot_data 


def metrics(offset):
  # Prepare the common variables
  REPLICATE, DATES, POPULATION, FAILURES = 0, 1, 2, 6
  DAYS = [90, 180, 270, 365, 545, 730]

  ndx = 0
  ntf, ntf_per_100 = [], []
  for days in DAYS:
    # Load the data and filter it to the subset indicated by the offset
    replicates = pd.read_csv('../Analysis/data/genotype_dataset/rwa-cycling-{}.csv'.format(days), header = None)
    dates = replicates[DATES].unique().tolist()
    replicates = replicates[(replicates[DATES] >= dates[offset * 12]) & (replicates[DATES] <= dates[-1])]
    
    # Apply the calculation to each replicate
    ntf.append([])
    ntf_per_100.append([])
    for replicate in replicates[REPLICATE].unique().tolist():
      # Filter some more for performance
      data = replicates[replicates[REPLICATE] == replicate]

      # Gather the per replicate data
      ntf[ndx].append(sum(data[FAILURES]))
      ntf_per_100[ndx].append(round(((sum(data[FAILURES]) / np.mean(data[POPULATION])) / 5) * 100, 3))

    # Update our index
    ndx += 1
    
  # Prepare the figure
  matplotlib.rc_file('matplotlibrc-line')
  figure, axes = plt.subplots(1, 2)

  # Prepare the NTF box plot
  axes[0].boxplot(ntf)
  axes[0].set_ylabel('Absolute Count')
  axes[0].set_xlabel('Rotation Days')
  axes[0].set_xticklabels(DAYS)
  
  # Prepare the NTF per 100 box plot
  axes[1].boxplot(ntf_per_100)
  axes[1].set_ylabel('Per 100 Population')
  axes[1].set_xlabel('Rotation Days')
  axes[1].set_xticklabels(DAYS)
  
  # Set the main title and save
  fig = plt.gcf()
  fig.suptitle('Number of Treatment Failures, {} years'.format(abs(offset)))
  plt.savefig('plots/metrics - {} years.png'.format(abs(offset)))
  plt.close()


def plot(plot_type, path, ylabel):
  def plot_data(data, ax):
    # Find the bounds of the data
    upper = np.percentile(data, 75, axis=0)
    median = np.percentile(data, 50, axis=0)
    lower = np.percentile(data, 25, axis=0)
  
    # Add the data to the subplot
    ax.plot(dates, median)
    color = scale_luminosity(ax.lines[-1].get_color(), 1)
    ax.fill_between(dates, lower, upper, alpha=0.5, facecolor=color)
    
    # Return the minima and maxima of the data
    return min(lower), max(upper)
  
  # Prepare the figure
  matplotlib.rc_file('matplotlibrc-line')
  figure, axes = plt.subplots(2, 3)
  ymin, ymax = sys.maxsize, 0
  
  row, col = 0, 0
  for days in [90, 180, 270, 365, 545, 730]:
    # Load the data, format the dates, and plot
    dates, frequency = load('../Analysis/data/{}/rwa-cycling-{}.csv'.format(path, days), plot_type)
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]  
    ranges = plot_data(frequency, axes[row, col])
    axes[row, col].title.set_text('{} days'.format(days))
    
    # Update the y-axis ranges
    ymin = min(ymin, ranges[0])
    ymax = max(ymax, ranges[1])
    
    # Move to the next subplot
    row, col = increment(row, col)
      
  # Update the figures
  for row in [0, 1]:
    for col in [0, 1, 2]:
      if col == 0:
        plt.sca(axes[row, col])
        plt.ylabel(ylabel)
        
      # Format the axis bounds
      start = 2023
      if plot_type in ['frequency', 'failures', 'pfpr']: start = 2014
      axes[row, col].set_xlim([datetime.datetime(start, 1, 1), max(dates)])
      axes[row, col].set_ylim([math.floor(ymin), math.ceil(ymax)])
    
  # Set the main label and save the plot
  fig = plt.gcf()
  fig.suptitle('DHA-PPQ then AL Cycling')
  plt.savefig('plots/{}.png'.format(plot_type))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-m', action='store', dest='metrics', help='The number of years (from end of dataset) to calculate metrics for')
  parser.add_argument('-p', action='store', dest='plot', help='The data to plot, values depend on the plot type')
  parser.add_argument('-t', action='store', dest='type', default='line', help='Plot type, either line (default) or box')
  args = parser.parse_args()

  if args.metrics:    
    metrics(-int(args.metrics))
  elif args.type == 'line':
    if args.plot == 'frequency': plot('frequency', 'datasets', '561H Frequency')
    elif args.plot == 'failures': plot('failures', 'datasets', 'Treatment Failures')
    elif args.plot == 'pfpr': plot('pfpr', 'genotype_dataset', '$Pf$PR$_{2-10}$')
    elif args.plot == 'ppq': plot('ppq', 'genotype_dataset', 'Plasmepsin Double Copy Frequency')
    elif args.plot == 'double': plot('double', 'genotype_dataset', 'Double Mutant Frequency')
    else: sys.exit('Unknown plot type, {}'.format(args.plot))
  elif args.type == 'box':
    box_plot('datasets', args.plot, offset=12*9)
  else:
    sys.exit('Unknown type argument, {}'.format(args.type))
