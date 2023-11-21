#!/usr/bin/env python3

# rwa_plot_districts.py
#
# Basic plotter for district policy interventions.
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

LABELS = {
  'baseline': ['Status Quo', '#bdd7e7'],
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


def load_all_datasets():
  datasets = {}
  for file in os.listdir(DATASETS_PATH):  
    key = file.replace('rwa-', '').replace('.csv', '')
    datasets[key] = load_dataset(os.path.join(DATASETS_PATH, file))
  return datasets, datasets[key].days.unique()

def load_dataset(filename):
  REPLICATES, DATES, INFECTIONS, WEIGHTED, TREATMENTS, FAILURES = 1, 2, 4, 8, 9, 10

  # Check to see if the cache exists, load and return if it does
  cache = os.path.join(CACHE_DIRECTORY, os.path.split(filename)[-1].replace('.csv', '') + '-cache.csv')
  if os.path.exists(cache):
    print('Loading cache for {} ...'.format(filename))
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


def annual(field):
  print('Preparing annual data on field, {}'.format(field))
  data, dates = load_all_datasets()
  for endpoint, bounds in ENDPOINTS.items():
    range = dates[bounds[0]:bounds[1]]
    
    # Offer some validation that this is the correct bounds
    date = datetime.datetime(MODEL_YEAR, 1, 1)
    print('{} Year: {:%Y-%m} to {:%Y-%m}'.format(endpoint,
      date + datetime.timedelta(days=int(range[0])),
      date + datetime.timedelta(days=int(range[-1]))))
    
    # Prepare the actual plot
    filename = '{}-{}-year.png'.format(field, bounds[2])
    if field == 'percent-failures':
      plot_percent_failures(data, range, filename)
    else:
      plot_field(data, range, field, filename)

def plot_percent_failures(data, dates, filename):
  # Start by generating the plot data
  records, labels, colors = [], [], []
  for key, format in LABELS.items():
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
  
  # Format the plot for the data
  axis.set_yticklabels(labels)
  axis.xaxis.set_major_formatter(ticker.PercentFormatter())      
  axis.set_xlabel('Percent Treatment Failure')
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()  

def plot_field(data, dates, field, filename):
  # Start by generating the plot data
  records, labels, colors = [], [], []
  for key, format in LABELS.items():
    # Process each replicate
    row = []
    for replicate in data[key].replicate.unique():
      subset = data[key][data[key].replicate == replicate]
      row.append(np.sum(subset[(subset.days >= dates[0]) & (subset.days <= dates[-1])][field]))
    
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
  
  # Format the plot for the data
  axis.set_yticklabels(labels)
  axis.set_xlabel(field.capitalize())
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()  


def frequencies():
  print('Preparing 561H frequencies...')
  data, dates = load_all_datasets()
  for endpoint, bounds in ENDPOINTS.items():
    range = dates[bounds[0]:bounds[1]]

    # Offer some validation that this the correct bounds  
    date = datetime.datetime(MODEL_YEAR, 1, 1)
    print('{} Year: {:%Y-%m}'.format(endpoint, date + datetime.timedelta(days=int(range[-1]))))        

    # Prepare the actual plot
    filename = 'frequency-{}-year.png'.format(bounds[2])
    plot_frequencies(data, range[-1], filename)

def plot_frequencies(data, date, filename):
  # Start by generating the data to plot
  records, labels, colors = [], [], []
  for key, format in LABELS.items():
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
  axis.set_xlim([0, 1])
  axis.set_xlabel('561H Frequency')
  axis.set_yticklabels(labels)
  
  # Save the plot
  plt.savefig(os.path.join(PLOTS_DIRECTORY, filename))
  plt.close()


if __name__ == '__main__':
  os.makedirs(CACHE_DIRECTORY, exist_ok=True)
  os.makedirs(PLOTS_DIRECTORY, exist_ok=True)
  frequencies()
  annual('treatments')
  annual('percent-failures')