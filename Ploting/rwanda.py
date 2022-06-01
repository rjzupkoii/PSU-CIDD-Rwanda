# rwanda.py
#
# This file contains common properties for Rwanda and associated reporting.

# Districts in Rwanda, keyed for the GIS data
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../PSU-CIDD-MaSim-Support/Python/include')
from plotting import scale_luminosity


DISTRICTS = {
    1  : 'Bugesera',
    2  : 'Gatsibo',
    3  : 'Kayonza',         # Studies
    4  : 'Kirehe',
    5  : 'Ngoma',
    6  : 'Nyagatare',
    7  : 'Rwamagana',
    8  : 'Gasabo',          # Studies / Spiked
    9  : 'Kicukiro',        # Studies
    10 : 'Nyarugenge',      # Studies
    11 : 'Burera',
    12 : 'Gakenke',
    13 : 'Gicumbi',
    14 : 'Musanze',
    15 : 'Rulindo',
    16 : 'Gisagara',
    17 : 'Huye',            # Studies
    18 : 'Kamonyi',
    19 : 'Muhanga',
    20 : 'Nyamagabe',
    21 : 'Nyanza',
    22 : 'Nyaruguru',
    23 : 'Ruhango',
    24 : 'Karongi',
    25 : 'Ngororero',
    26 : 'Nyabihu',
    27 : 'Nyamasheke',
    28 : 'Rubavu',
    29 : 'Rusizi',
    30 : 'Rutsiro'
}

# Start of simulation
STUDYDATE = '2003-1-1'

# Date when the policy change is introduced in the simulation
POLICYDATE = datetime.datetime(2023, 1, 1)

# Reference date for replicate validation, note we are using the minimal
# frequency for the reject threshold since there may have been spatial 
# clustering when the study was performed.
REFERENCEDATE = datetime.datetime(2014, 9, 1)
REFERENCEDISTRICT = 8
REFERENCEFREQUENCY = 0.01

# The path for the summary data set
DATA_PATH = '../Analysis/data/datasets'

# The various configurations that are run for the simulation
CONFIGURATIONS = {
    # Status quo
    'rwa-pfpr-constant.csv'        : 'Status Quo',

    # Artesunate Extension
    'rwa-ae-al-4.csv'              : 'AL (Four Days)',
    'rwa-ae-al-3-1-1.csv'          : 'AL 3-1-1',
    'rwa-ae-al-3-1-2.csv'          : 'AL 3-1-2',

    'rwa-ae-al-5.csv'              : 'AL (Five Days)',
    'rwa-ae-al-3-2-1.csv'          : 'AL 3-2-1',
    'rwa-ae-al-3-2-2.csv'          : 'AL 3-2-2',

    # Multiple First-line Therapies
    'rwa-mft-al-asaq-0.25.csv'     : 'MFT AL (75%) + ASAQ (25%)',
    'rwa-mft-al-asaq.csv'          : 'MFT AL (50%) + ASAQ (50%)',
    'rwa-mft-al-asaq-0.75.csv'     : 'MFT AL (25%) + ASAQ (75%)',
    
    'rwa-mft-al-dhappq-0.25.csv'   : 'MFT AL (75%) + DHA-PPQ (25%)',
    'rwa-mft-al-dhappq.csv'        : 'MFT AL (50%) + DHA-PPQ (50%)',
    'rwa-mft-al-dhappq-0.75.csv'   : 'MFT AL (25%) + DHA-PPQ (75%)',
    
    'rwa-mft-asaq-dhappq-0.25.csv' : 'MFT ASAQ (75%) + DHA-PPQ (25%)',
    'rwa-mft-asaq-dhappq.csv'      : 'MFT ASAQ (50%) + DHA-PPQ (50%)',
    'rwa-mft-asaq-dhappq-0.75.csv' : 'MFT ASAQ (25%) + DHA-PPQ (75%)',
    
    # AL Replacement
    'rwa-replacement-asaq.csv'     : '100% ASAQ Deployment',
    'rwa-replacement-dhappq.csv'   : '100% DHA-PPQ Deployment',

    # Rotations
    'rwa-rotation-al-3.csv'        : 'DHA-PPQ (3 years), MFT AL (50%) + ASAQ (50%)',
    'rwa-rotation-al-5.csv'        : 'DHA-PPQ (3 years), MFT AL, 5 days (50%) + ASAQ (50%)',

    # Triple-ACT
    'rwa-tact-alaq.csv'            : 'TACT AL + AQ',
    'rwa-tact-dhappqmq.csv'        : 'TACT DHA-PPQ + PQ',

    # NMCP
    'rwa-nmcp-1a.csv'              : 'NMCP Scenario 1a',
    'rwa-nmcp-1b.csv'              : 'NMCP Scenario 1b',
    'rwa-nmcp-1c.csv'              : 'NMCP Scenario 1c',
    'rwa-nmcp-2a.csv'              : 'NMCP Scenario 2a',
    'rwa-nmcp-3c.csv'              : 'NMCP Scenario 3c',
    'rwa-nmcp-4c.csv'              : 'NMCP Scenario 4c',

    # Compliance, AL, three days
    'rwa-al-3-high.csv'     : 'AL, 3 days, High',
    'rwa-al-3-moderate.csv' : 'AL, 3 days, Moderate',
    'rwa-al-3-low.csv'      : 'AL, 3 days, Low',

    # Compliance, AL, four days
    'rwa-al-4-high.csv'     : 'AL, 4 days, High',
    'rwa-al-4-moderate.csv' : 'AL, 4 days, Moderate',
    'rwa-al-4-low.csv'      : 'AL, 4 days, Low',

    # Compliance, AL, five days
    'rwa-al-5-high.csv'     : 'AL, 5 days, High',
    'rwa-al-5-moderate.csv' : 'AL, 5 days, Moderate',
    'rwa-al-5-low.csv'      : 'AL, 5 days, Low',

    # Compliance, ASAQ
    'rwa-asaq-high.csv'     : 'ASAQ, High',
    'rwa-asaq-moderate.csv' : 'ASAQ, Moderate',
    'rwa-asaq-low.csv'      : 'ASAQ, Low',

    # Compliance, DHA-PPQ
    'rwa-dhappq-high.csv'     : 'DHA-PPQ, High',
    'rwa-dhappq-moderate.csv' : 'DHA-PPQ, Moderate',
    'rwa-dhappq-low.csv'      : 'DHA-PPQ, Low',
}

# Index defintions for spikes
SPIKE_DISTRICT, SPIKE_LABEL, SPIKE_X, SPIKE_Y = range(4)

# Points at which 561H was spiked into the population
SPIKES = np.array([
    # Uwimana et al. 2020 
    [8, 'Gasabo (0.12069)', datetime.datetime(2014,9,30), 0.12069],
    [3, 'Kayonza (0.00746)', datetime.datetime(2015,9,30), 0.00746],
    [8, 'Gasabo (0.0603)', datetime.datetime(2015,9,30), 0.0603],
    
    # Uwimana et al. 2021
    [8, 'Gasabo (0.19608)', datetime.datetime(2018,9,30), 0.19608],
    [3, 'Kayonza (0.09756)', datetime.datetime(2018,9,30), 0.09756],

    # Straimer et al. 2021, note 
    [8, 'Kigali City (0.21918)', datetime.datetime(2019,9,30), 0.21918],
    [9, 'Kigali City (0.21918)', datetime.datetime(2019,9,30), 0.21918],
    [10, 'Kigali City (0.21918)', datetime.datetime(2019,9,30), 0.21918],

    # Bergmann et al. 2021 
    [17, 'Hyue (0.12069)', datetime.datetime(2019,9,30), 0.12121],
])

# Index definitions for the four-panel report layout
REPORT_INDEX, REPORT_ROW, REPORT_COLUMN, REPORT_YLABEL = range(4)

# Four-panel report layout
REPORT_LAYOUT = {
    'cases': [5, 0, 0, 'Clinical Cases'],
    'failures': [9, 1, 0, 'Treatment Failures'], 
    'frequency' : [-1, 0, 1, '561H Frequency'],
    'carriers': [10, 1, 1, 'Individuals with 561H Clones']
}


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


def plot_summary(title, dates, figureData, district = None, studies = False, extension = 'png', prefix = None):
    # Format the dates
    startDate = datetime.datetime.strptime(STUDYDATE, "%Y-%m-%d")
    dates = [startDate + datetime.timedelta(days=x) for x in dates]

    # Prepare the plots
    matplotlib.rc_file('matplotlibrc-line')
    figure, axes = plt.subplots(2, 2)

    for key in REPORT_LAYOUT:
        row, col = REPORT_LAYOUT[key][REPORT_ROW], REPORT_LAYOUT[key][REPORT_COLUMN]

        # Load the data and calculate the bounds      
        data = figureData[key]  
        upper = np.percentile(data, 75, axis=0)
        median = np.percentile(data, 50, axis=0)
        lower = np.percentile(data, 25, axis=0)

        # Add the data to the subplot
        axes[row, col].plot(dates, median)
        color = scale_luminosity(axes[row, col].lines[-1].get_color(), 1)
        axes[row, col].fill_between(dates, lower, upper, alpha=0.5, facecolor=color)

        # Label the axis as needed
        plt.sca(axes[row, col])
        plt.ylabel(REPORT_LAYOUT[key][REPORT_YLABEL])
        if row == 1:
            plt.xlabel('Model Year')

        # Add the 561H data points if requested
        if studies and key == 'frequency':
            for id, label, x, y in SPIKES:
                if district == id:
                    plt.scatter(x, y, color='black', s=50)
                    match = re.search('(\d\.\d*)', label)
                    plt.annotate(match.group(0), (x, y), textcoords='offset points', xytext=(0,10), ha='center', fontsize=18)

    # Format the subplots
    for ax in axes.flat:
        ax.set_xlim([min(dates), max(dates)])

    # Format and save the plot
    if district != None:
        figure.suptitle('{}\n{}, Rwanda'.format(title, DISTRICTS[district]))
        imagefile = 'plots/{0}/{3}{1} - {0}.{2}'.format(title, DISTRICTS[district], extension, prefix)
        os.makedirs('plots/{}'.format(title), exist_ok=True)
    else:
        figure.suptitle('{}\nRwanda'.format(title))
        imagefile = 'plots/{2}Summary - {0}.{1}'.format(title, extension, prefix)

    # Save the plot based upon the extension
    if imagefile.endswith('tif'):
        plt.savefig(imagefile, dpi=300, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    else:
        plt.savefig(imagefile)        
    plt.close()