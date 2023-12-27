#!/usr/bin/env python3

# rwa_plot_districts.py
#
# Basic plotter for district policy interventions.
# 
# There's a lot of cut-and-paste code taking place here around setting the 
# plots up - longer term it should be refactored to something a bit more
# streamlined.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd
import seaborn as sb
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from utility import progressBar

CACHE_DIRECTORY = 'cache'
DATASETS_PATH = '../Analysis/data/datasets'
PLOTS_DIRECTORY = 'plots'
VIOLIN_CONFIGURATION = 'matplotlibrc-violin'

MODEL_YEAR = 2003

ENDPOINTS = {
  # Endpoint : First Date Offset, Last Date Offset, Numeric Value
  'Three' : [-96, -84, 3],
  'Five'  : [-72, -60, 5],
  'Ten'   : [-12, None, 10]
}

FIXED_LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'fixed-frequency-0.25-al': ['By frequency, 25% AL', '#6baed6'],
  'fixed-frequency-0.5-al': ['50% AL', '#6baed6'],
  'fixed-frequency-0.75-al': ['75% AL', '#6baed6'],
  'fixed-frequency-0.25-dhappq': ['25% DHA-PPQ', '#6baed6'],
  'fixed-frequency-0.5-dhappq': ['50% DHA-PPQ', '#6baed6'],
  'fixed-frequency-0.75-dhappq': ['75% DHA-PPQ', '#6baed6'],
  'fixed-incidence-0.25-al': ['By incidence, 25% AL', '#bae4b3'],
  'fixed-incidence-0.5-al': ['50% AL', '#bae4b3'],
  'fixed-incidence-0.75-al': ['75% AL', '#bae4b3'],
  'fixed-incidence-0.25-dhappq': ['25% DHA-PPQ', '#bae4b3'],
  'fixed-incidence-0.5-dhappq': ['50% DHA-PPQ', '#bae4b3'],
  'fixed-incidence-0.75-dhappq': ['75% DHA-PPQ', '#bae4b3'],
  'fixed-pfpr2to10-0.25-al': ['By PfPR 2-10, 25% AL', '#df65b0'],
  'fixed-pfpr2to10-0.5-al': ['50% AL', '#df65b0'],
  'fixed-pfpr2to10-0.75-al': ['75% AL', '#df65b0'],
  'fixed-pfpr2to10-0.25-dhappq': ['25% DHA-PPQ', '#df65b0'],
  'fixed-pfpr2to10-0.5-dhappq': ['50% DHA-PPQ', '#df65b0'],
  'fixed-pfpr2to10-0.75-dhappq': ['75% DHA-PPQ', '#df65b0'],
}

FIXED_INCIDENCE_SENSITIVITY = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'fixed-incidence-0.75-al': ['75% AL (1x)', '#bae4b3'],
  'fixed-incidence-0.75-al-10x': ['75% AL (10x)', '#bae4b3'],
  'fixed-incidence-0.75-al-100x': ['75% AL (100x)', '#bae4b3'],
  'fixed-incidence-0.25-dhappq': ['25% DHA-PPQ (1x)', '#df65b0'],
  'fixed-incidence-0.25-dhappq-10x': ['25% DHA-PPQ (10x)', '#df65b0'],
  'fixed-incidence-0.25-dhappq-100x': ['25% DHA-PPQ (100x)', '#df65b0'],
}

ONE_YEAR_ROTATION_LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'rotation-frequency-0.25-al-1y': ['By frequency, 25% AL', '#6baed6'],
  'rotation-frequency-0.5-al-1y': ['50% AL', '#6baed6'],
  'rotation-frequency-0.75-al-1y': ['75% AL', '#6baed6'],
  'rotation-frequency-0.25-dhappq-1y': ['25% DHA-PPQ', '#6baed6'],
  'rotation-frequency-0.5-dhappq-1y': ['50% DHA-PPQ', '#6baed6'],
  'rotation-frequency-0.75-dhappq-1y': ['75% DHA-PPQ', '#6baed6'],
  'rotation-incidence-0.25-al-1y': ['By incidence, 25% AL', '#bae4b3'],
  'rotation-incidence-0.5-al-1y': ['50% AL', '#bae4b3'],
  'rotation-incidence-0.75-al-1y': ['75% AL', '#bae4b3'],
  'rotation-incidence-0.25-dhappq-1y': ['25% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.5-dhappq-1y': ['50% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.75-dhappq-1y': ['75% DHA-PPQ', '#bae4b3'],
  'rotation-pfpr2to10-0.25-al-1y': ['By PfPR 2-10, 25% AL', '#df65b0'],
  'rotation-pfpr2to10-0.5-al-1y': ['50% AL', '#df65b0'],
  'rotation-pfpr2to10-0.75-al-1y': ['75% AL', '#df65b0'],
  'rotation-pfpr2to10-0.25-dhappq-1y': ['25% DHA-PPQ', '#df65b0'],
  'rotation-pfpr2to10-0.5-dhappq-1y': ['50% DHA-PPQ', '#df65b0'],
  'rotation-pfpr2to10-0.75-dhappq-1y': ['75% DHA-PPQ', '#df65b0'],
  'rotation-random-0.25-al-1y': ['Random Allocation, 25% AL', '#6baed6'],
  'rotation-random-0.5-al-1y': ['50% AL', '#6baed6'],
  'rotation-random-0.75-al-1y': ['75% AL', '#6baed6'],
  'rotation-random-0.25-dhappq-1y': ['25% DHA-PPQ', '#6baed6'],
  'rotation-random-0.5-dhappq-1y': ['50% DHA-PPQ', '#6baed6'],
  'rotation-random-0.75-dhappq-1y': ['75% DHA-PPQ', '#6baed6'],  
}

ONE_YEAR_POLICY_OPTIONS_LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'rotation-incidence-0.25-al-1y': ['By incidence, 25% AL', '#bae4b3'],
  'rotation-incidence-0.5-al-1y': ['50% AL', '#bae4b3'],
  'rotation-incidence-0.75-al-1y': ['75% AL', '#bae4b3'],
  'rotation-incidence-0.25-dhappq-1y': ['25% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.5-dhappq-1y': ['50% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.75-dhappq-1y': ['75% DHA-PPQ', '#bae4b3'],
  'rotation-random-0.25-al-1y': ['Random Allocation, 25% AL', '#6baed6'],
  'rotation-random-0.5-al-1y': ['50% AL', '#6baed6'],
  'rotation-random-0.75-al-1y': ['75% AL', '#6baed6'],
  'rotation-random-0.25-dhappq-1y': ['25% DHA-PPQ', '#6baed6'],
  'rotation-random-0.5-dhappq-1y': ['50% DHA-PPQ', '#6baed6'],
  'rotation-random-0.75-dhappq-1y': ['75% DHA-PPQ', '#6baed6'],  
}

RANDOM_LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'rotation-random-0.25-al': ['Random Allocation, 25% AL', '#6baed6'],
  'rotation-random-0.5-al': ['50% AL', '#6baed6'],
  'rotation-random-0.75-al': ['75% AL', '#6baed6'],
  'rotation-random-0.25-dhappq': ['25% DHA-PPQ', '#6baed6'],
  'rotation-random-0.5-dhappq': ['50% DHA-PPQ', '#6baed6'],
  'rotation-random-0.75-dhappq': ['75% DHA-PPQ', '#6baed6'],
}

ROTATION_LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
  'mft-al-dhappq-0.25': ['75% AL, 25% DHA-PPQ', '#bdd7e7'],
  'rotation-frequency-0.25-al': ['By frequency, 25% AL', '#6baed6'],
  'rotation-frequency-0.5-al': ['50% AL', '#6baed6'],
  'rotation-frequency-0.75-al': ['75% AL', '#6baed6'],
  'rotation-frequency-0.25-dhappq': ['25% DHA-PPQ', '#6baed6'],
  'rotation-frequency-0.5-dhappq': ['50% DHA-PPQ', '#6baed6'],
  'rotation-frequency-0.75-dhappq': ['75% DHA-PPQ', '#6baed6'],
  'rotation-incidence-0.25-al': ['By incidence, 25% AL', '#bae4b3'],
  'rotation-incidence-0.5-al': ['50% AL', '#bae4b3'],
  'rotation-incidence-0.75-al': ['75% AL', '#bae4b3'],
  'rotation-incidence-0.25-dhappq': ['25% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.5-dhappq': ['50% DHA-PPQ', '#bae4b3'],
  'rotation-incidence-0.75-dhappq': ['75% DHA-PPQ', '#bae4b3'],
  'rotation-pfpr2to10-0.25-al': ['By PfPR 2-10, 25% AL', '#df65b0'],
  'rotation-pfpr2to10-0.5-al': ['50% AL', '#df65b0'],
  'rotation-pfpr2to10-0.75-al': ['75% AL', '#df65b0'],
  'rotation-pfpr2to10-0.25-dhappq': ['25% DHA-PPQ', '#df65b0'],
  'rotation-pfpr2to10-0.5-dhappq': ['50% DHA-PPQ', '#df65b0'],
  'rotation-pfpr2to10-0.75-dhappq': ['75% DHA-PPQ', '#df65b0'],
}


def load_datasets(prefix):
  datasets = {}
  for file in os.listdir(DATASETS_PATH):  
    if not any(value in file for value in ['baseline', 'mft']) and prefix not in file: continue
    key = file.replace('rwa-', '').replace('.csv', '')
    datasets[key] = load_dataset(os.path.join(DATASETS_PATH, file))
  return datasets, datasets[key].days.unique()

def load_dataset(filename):
  REPLICATES, DATES, INFECTIONS, WEIGHTED, TREATMENTS, FAILURES = 1, 2, 4, 8, 9, 10

  # Track what we've loaded while the program is running to reduce the amount of output
  if not hasattr(load_dataset, "loaded"):
    load_dataset.loaded = []

  # Check to see if the cache exists, load and return if it does
  cache = os.path.join(CACHE_DIRECTORY, os.path.split(filename)[-1].replace('.csv', '') + '-cache.csv')
  if os.path.exists(cache):
    if not cache in load_dataset.loaded:
      print('Loading cache for {} ...'.format(filename))
      load_dataset.loaded.append(cache)
    return pd.read_csv(cache)

  # Inform the user
  print('Create cache for {} ...'.format(filename))

  # The cache does not exist, start by loading the full dataset
  data = pd.read_csv(filename, header=None)
  dates = data[DATES].unique().tolist()
  replicates = data[REPLICATES].unique()

  # Parse the data into a list of dictionaries
  rows = []
  for replicate in replicates:
    for date in dates:
      # Filter on the combination
      subset = data[(data[REPLICATES] == replicate) & (data[DATES] == date)]

      # Parse the items into a row, append it and update the status
      row = {
        'replicate': replicate,
        'days': date,
        'treatments': np.sum(subset[TREATMENTS]),
        'failures': np.sum(subset[FAILURES]),
        'infections': np.sum(subset[INFECTIONS]),
        'weighted': np.sum(subset[WEIGHTED])
      }
      rows.append(row)
      progressBar(len(rows), len(dates) * len(replicates))
  
  # Copy the data to the data frame, save, and return the data
  df = pd.DataFrame(rows)
  df.to_csv(cache)
  return df        


def annual(field, prefix, report):
  # Load the data that we need
  data, dates = load_datasets(prefix)

  print('Preparing {} annual data on field, {}'.format(prefix, field))
  for endpoint, bounds in ENDPOINTS.items():
    range = dates[bounds[0]:bounds[1]]
    
    # Offer some validation that this is the correct bounds
    date = datetime.datetime(MODEL_YEAR, 1, 1)
    print('{} Year: {:%Y-%m} to {:%Y-%m}'.format(endpoint,
      date + datetime.timedelta(days=int(range[0])),
      date + datetime.timedelta(days=int(range[-1]))))
    
    # Prepare the actual plot
    title = '{} Strategy - {} Years'.format(prefix.capitalize(), endpoint)
    filename = '{}-{}-{}-year.png'.format(prefix, field, bounds[2])
    if field == 'percent-failures':
      plot_percent_failures(data, range, title, filename, report)
    else:
      plot_field(data, range, field, title, filename, report)

def plot_percent_failures(data, dates, title, filename, report):
  # Start by generating the plot data
  records, labels, colors = [], [], []
  for key, format in report.items():
    # Process each replicate
    row = []
    for replicate in data[key].replicate.unique():
      subset = data[key][data[key].replicate == replicate]
      treatments = np.sum(subset[(subset.days >= dates[0]) & (subset.days <= dates[-1])].treatments)
      failures = np.sum(subset[(subset.days >= dates[0]) & (subset.days <= dates[-1])].failures)      
      row.append((failures / treatments) * 100.0)
    
    # Append the processed data
    labels.append(format[0])
    colors.append(format[1])
    records.append(row)
    
  # Generate the plot
  matplotlib.rc_file(VIOLIN_CONFIGURATION)
  figure, axis = plt.subplots()
  violin = sb.violinplot(data=records, palette=colors, cut=0, scale='width', inner=None, linewidth=0.5, orient='h')
  sb.boxplot(data=records, palette=colors, width=0.2, boxprops={'zorder' : 2}, orient='h')
  sb.despine(top=True, right=True, left=True, bottom=True)
  
  # Scale the alpha channel for the violin plot
  for item in violin.collections: item.set_alpha(0.5)
  
  # Set the x-bounds of the plot, this manually set via earlier plots
  axis.set_xbound([0.0, 50.0])

  # Format the plot for the data
  plt.title(title)
  axis.set_yticklabels(labels)
  axis.xaxis.set_major_formatter(ticker.PercentFormatter())      
  axis.set_xlabel('Percent Treatment Failure')
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()  

def plot_field(data, dates, field, title, filename, report):
  # Start by generating the plot data
  records, labels, colors = [], [], []
  for key, format in report.items():
    # Process each replicate
    row = []
    for replicate in data[key].replicate.unique():
      subset = data[key][data[key].replicate == replicate]
      row.append(np.sum(subset[(subset.days >= dates[0]) & (subset.days <= dates[-1])][field]) / 12)
    
    # Append the processed data
    labels.append(format[0])
    colors.append(format[1])
    records.append(row)
    
  # Generate the plot
  matplotlib.rc_file(VIOLIN_CONFIGURATION)
  figure, axis = plt.subplots()
  violin = sb.violinplot(data=records, palette=colors, cut=0, scale='width', inner=None, linewidth=0.5, orient='h')
  sb.boxplot(data=records, palette=colors, width=0.2, boxprops={'zorder' : 2}, orient='h')
  sb.despine(top=True, right=True, left=True, bottom=True)
  
  # Scale the alpha channel for the violin plot
  for item in violin.collections: item.set_alpha(0.5)

  # Set the x-bounds of the plot, this manually set via earlier plots
  if field == 'treatments': axis.set_xbound([10000, 43000])

  # Format the plot for the data
  plt.title(title)
  axis.set_yticklabels(labels)
  axis.set_xlabel(field.capitalize() + ' (12-month average)')
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()  


def frequencies(prefix, report):
  # Load the data that we need
  data, dates = load_datasets(prefix)

  print('Preparing {} 561H frequencies...'.format(prefix))
  for endpoint, bounds in ENDPOINTS.items():
    range = dates[bounds[0]:bounds[1]]

    # Offer some validation that this the correct bounds  
    date = datetime.datetime(MODEL_YEAR, 1, 1)
    print('{} Year: {:%Y-%m}'.format(endpoint, date + datetime.timedelta(days=int(range[-1]))))        

    # Prepare the actual plot
    title = '{} Strategy - {} Years'.format(prefix.capitalize(), endpoint)
    filename = '{}-frequency-{}-year.png'.format(prefix, bounds[2])
    plot_frequencies(data, range[-1], title, filename, report)

def plot_frequencies(data, date, title, filename, report):
  # Start by generating the data to plot
  records, labels, colors = [], [], []
  for key, format in report.items():
    data[key]['frequency'] = data[key].weighted / data[key].infections
    records.append(data[key][data[key].days == date].frequency)
    labels.append(format[0])
    colors.append(format[1])

  # Generate the plot
  matplotlib.rc_file(VIOLIN_CONFIGURATION)
  figure, axis = plt.subplots()
  violin = sb.violinplot(data=records, palette=colors, cut=0, scale='width', inner=None, linewidth=0.5, orient='h')
  sb.boxplot(data=records, palette=colors, width=0.2, boxprops={'zorder' : 2}, orient='h')
  sb.despine(top=True, right=True, left=True, bottom=True)

  # Scale the alpha channel for the violin plot
  for item in violin.collections: item.set_alpha(0.5)

  # Format the plot for the data
  plt.title(title)
  axis.set_xlim([0, 1])
  axis.set_xlabel('561H Frequency')
  axis.set_yticklabels(labels)
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()


if __name__ == '__main__':
  os.makedirs(CACHE_DIRECTORY, exist_ok=True)
  os.makedirs(PLOTS_DIRECTORY, exist_ok=True)

  # # Generate the fixed plots
  # frequencies('fixed', FIXED_LABELS)
  # annual('treatments', 'fixed', FIXED_LABELS)
  # annual('percent-failures', 'fixed', FIXED_LABELS)

  # # Generate the rotation plots
  # frequencies('rotation', ROTATION_LABELS)
  # annual('treatments', 'rotation', ROTATION_LABELS)
  # annual('percent-failures', 'rotation', ROTATION_LABELS)  

  # # Generate the random plots
  # frequencies('random', RANDOM_LABELS)
  # annual('treatments', 'random', RANDOM_LABELS)
  # annual('percent-failures', 'random', RANDOM_LABELS)

  # # Generate all the one year rotation plots
  # frequencies('rotation', ONE_YEAR_ROTATION_LABELS)
  # annual('treatments', 'rotation', ONE_YEAR_ROTATION_LABELS)
  # annual('percent-failures', 'rotation', ONE_YEAR_ROTATION_LABELS)

  # # Generate all the realistic policy option plots
  # frequencies('rotation', ONE_YEAR_POLICY_OPTIONS_LABELS)
  # annual('treatments', 'rotation', ONE_YEAR_POLICY_OPTIONS_LABELS)
  # annual('percent-failures', 'rotation', ONE_YEAR_POLICY_OPTIONS_LABELS)

  # Generate all the movement sensitivity plots
  frequencies('incidence', FIXED_INCIDENCE_SENSITIVITY)
  annual('treatments', 'incidence', FIXED_INCIDENCE_SENSITIVITY)
  annual('percent-failures', 'incidence', FIXED_INCIDENCE_SENSITIVITY)