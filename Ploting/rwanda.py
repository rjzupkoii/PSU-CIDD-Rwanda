# rwanda.py
#
# This file contains common proprties for Rwanda and associated reporting.

# Districts in Rwanda, keyed for the GIS data
DISTRICTS = {
    1  : 'Bugesera',
    2  : 'Gatsibo',
    3  : 'Kayonza',         # Spiked
    4  : 'Kirehe',
    5  : 'Ngoma',
    6  : 'Nyagatare',
    7  : 'Rwamagana',
    8  : 'Gasabo',          # Spiked
    9  : 'Kicukiro',        # Spiked
    10 : 'Nyarugenge',      # Spiked
    11 : 'Burera',
    12 : 'Gakenke',
    13 : 'Gicumbi',
    14 : 'Musanze',
    15 : 'Rulindo',
    16 : 'Gisagara',
    17 : 'Hyue',            # Spiked
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
    'rwa-replacement-asaq.csv'     : '100% ASAQ Deployment'
}

# Index definitions for the four-panel report layout
REPORT_INDEX, REPORT_ROW, REPORT_COLUMN, REPORT_YLABEL = range(4)

# Four-panel report layout
REPORT_LAYOUT = {
    'cases': [5, 0, 0, 'Clinical Cases'],
    'failures': [9, 1, 0, 'Treatment Failures'], 
    'frequency' : [-1, 0, 1, '561H Frequency'],
    'carriers': [10, 1, 1, 'Individuals with 561H Clones']
}