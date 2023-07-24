#!/usr/bin env python3

# rwa_cycling.py
#
# Produce a basic plot of 561H frequency based upon the cycling timeframes.
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


def load(filename, plot_type):
  REPLICATE, DATES, INFECTIONS, WEIGHTED, TREATMENTS, TREATMENT_FAILURES = 1, 2, 4, 8, 9, 10
  
  # Load the data, calculate the frequency; note the unique dates, replicates
  data = pd.read_csv(filename, header = None)
  dates = data[DATES].unique().tolist()
  replicates = data[REPLICATE].unique().tolist()
  
  # Load the frequency from the data set
  count, plot_data = 0, []
  for replicate in replicates:
    byReplicate = data[data[REPLICATE] == replicate]
    temp = []
    for date in dates:
      byDate = byReplicate[byReplicate[DATES] == date]
      if plot_type == 'frequency':
        temp.append(sum(byDate[WEIGHTED]) / sum(byDate[INFECTIONS]))
      elif plot_type == 'failures':
        temp.append(sum(byDate[TREATMENT_FAILURES]) / sum(byDate[TREATMENTS]))
    if len(plot_data) != 0: plot_data = np.vstack((plot_data, temp))
    else: plot_data = temp
  
    # Update the progress bar
    count += 1
    progressBar(count, len(replicates))
  
  # Return the results
  return dates, plot_data 


def plot(plot_type, ylabel):
  def plot_data(data, ax):
    # Find the bounds of the data
    upper = np.percentile(data, 75, axis=0)
    median = np.percentile(data, 50, axis=0)
    lower = np.percentile(data, 25, axis=0)
  
    # Add the data to the subplot
    ax.plot(dates, median)
    color = scale_luminosity(ax.lines[-1].get_color(), 1)
    ax.fill_between(dates, lower, upper, alpha=0.5, facecolor=color)
  
  # Prepare the figure
  matplotlib.rc_file('matplotlibrc-line')
  figure, axes = plt.subplots(2, 3)

  row, col = 0, 0
  for days in [90, 180, 270, 365, 545, 730]:
    # Load the data, format the dates, and plot
    dates, frequency = load('../Analysis/data/datasets/rwa-cycling-{}.csv'.format(days), plot_type)
    startDate = datetime.datetime.strptime(rwanda.STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]  
    plot_data(frequency, axes[row, col])
    
    # Apply the formatting
    axes[row, col].title.set_text('{} days'.format(days))
    axes[row, col].set_ylim([0, 1])
    axes[row, col].set_xlim([datetime.datetime(2014, 1, 1), max(dates)])
    
    if col == 0:
      plt.sca(axes[row, col])
      plt.ylabel(ylabel)
    
    # Move to the next subplot
    col += 1
    if col % 3 == 0:
      row += 1
      col = 0
    
  # Set the main label and save the plot
  fig = plt.gcf()
  fig.suptitle('DHA-PPQ then Al Cycling')
  plt.savefig('{}.png'.format(plot_type))


if __name__ == '__main__':
  plot('frequency', '561H Frequency')
  plot('failures', 'Treatment Failures')
