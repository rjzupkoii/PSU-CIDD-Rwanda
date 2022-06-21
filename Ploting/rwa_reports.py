# rwa_reports.py
#
# This file contains the definitions of various reports for Rwanda.

STUDIES = {
    # Status Quo
    'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

    # Extend AL
    'rwa-ae-al-4.csv'              : ['AL, 4 days', '#bdd7e7'],
    'rwa-ae-al-5.csv'              : ['AL, 5 days', '#bdd7e7'],

    # Replace AL
    'rwa-replacement-asaq.csv'     : ['100% ASAQ', '#6baed6'],
    'rwa-replacement-dhappq.csv'   : ['100% DHA-PPQ', '#6baed6'],

    # AL / ASAQ MFT
    'rwa-mft-al-asaq-0.25.csv'     : ['AL (75%) + ASAQ (25%)', '#bae4b3'],
    'rwa-mft-al-asaq.csv'          : ['AL (50%) + ASAQ (50%)', '#bae4b3'],
    'rwa-mft-al-asaq-0.75.csv'     : ['AL (25%) + ASAQ (75%)', '#bae4b3'],

    # AL / DHA-PPQ MFT
    'rwa-mft-al-dhappq-0.25.csv'   : ['AL (75%) + DHA-PPQ (25%)', '#74c476'],
    'rwa-mft-al-dhappq.csv'        : ['AL (50%) + DHA-PPQ (50%)', '#74c476'],
    'rwa-mft-al-dhappq-0.75.csv'   : ['AL (25%) + DHA-PPQ (75%)', '#74c476'],

    # ASAQ / DHA-PPQ MFT
    'rwa-mft-asaq-dhappq-0.25.csv' : ['ASAQ (75%) + DHA-PPQ (25%)', '#31a354'],
    'rwa-mft-asaq-dhappq.csv'      : ['ASAQ (50%) + DHA-PPQ (50%)', '#31a354'],
    'rwa-mft-asaq-dhappq-0.75.csv' : ['ASAQ (25%) + DHA-PPQ (75%)', '#31a354'],

    # Rotate DHA-PPQ
    'rwa-rotation-al-3.csv'        : ['DHA-PPQ (3 years) / AL (50%) + ASAQ', '#d7b5d8'],
    'rwa-rotation-al-5.csv'        : ['DHA-PPQ (3 years) / AL, 5 days (50%) + ASAQ', '#d7b5d8'],

    # TACT
    'rwa-tact-alaq.csv'            : ['AL + AQ', '#df65b0'],
    'rwa-tact-dhappqmq.csv'        : ['DHA-PPQ + MQ', '#df65b0'],
}

COMPLIANCE = {
    # AL, three days
    'rwa-al-3-high.csv'     : ['AL, 3 days, High', '#117733'],
    'rwa-al-3-moderate.csv' : ['AL, 3 days, Moderate', '#58a070'],
    'rwa-al-3-low.csv'      : ['AL, 3 days, Low', '#a0c9ad'],

    # AL, four days
    'rwa-al-4-high.csv'     : ['AL, 4 days, High', '#44aa99'],
    'rwa-al-4-moderate.csv' : ['AL, 4 days, Moderate', '#7cc4b8'],
    'rwa-al-4-low.csv'      : ['AL, 4 days, Low', '#b4ddd6'],

    # AL, five days
    'rwa-al-5-high.csv'     : ['AL, 5 days, High', '#b4ddd6'],
    'rwa-al-5-moderate.csv' : ['AL, 5 days, Moderate', '#cbe7e2'],
    'rwa-al-5-low.csv'      : ['AL, 5 days, Low', '#e1f1ef'],

    # ASAQ
    'rwa-asaq-high.csv'     : ['ASAQ, High', '#cc6677'],
    'rwa-asaq-moderate.csv' : ['ASAQ, Moderate', '#db94a0'],
    'rwa-asaq-low.csv'      : ['ASAQ, Low', '#ebc2c9'],

    # DHA-PPQ
    'rwa-dhappq-high.csv'     : ['DHA-PPQ, High', '#882255'],
    'rwa-dhappq-moderate.csv' : ['DHA-PPQ, Moderate', '#ac6488'],
    'rwa-dhappq-low.csv'      : ['DHA-PPQ, Low', '#cfa7bb'],
}

# NMCP scenarios
NMCP = {
    # Status Quo
    'rwa-pfpr-constant.csv' : ['Status Quo', '#88CCEE'],

    # Scenario 1, MFT AL (5-day) and DHA-PPQ
    'rwa-nmcp-1a.csv'       : ['1a', '#44AA99'],
    'rwa-nmcp-1b.csv'       : ['1b', '#44AA99'],
    'rwa-nmcp-1c.csv'       : ['1c', '#44AA99'],

    # Scenario 2, sensitivity analysis for scenario 1a
    'rwa-nmcp-2a.csv'       : ['2a', '#117733'],

    # Scenario 3c, MFT AL (5-day), DHA-PPQ, and ASAQ / Prolonged ASAQ adoption
    'rwa-nmcp-3c.csv'       : ['3c', '#DDCC77'],

    # Scenario 4c, MFT AL (5-day), DHA-PPQ, and ASAQ / Rapid ASAQ adoption
    'rwa-nmcp-4c.csv'       : ['4c', '#A691AE'],
}