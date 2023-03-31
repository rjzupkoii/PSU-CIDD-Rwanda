# rwa_reports.py
#
# This file contains the definitions of various reports for Rwanda.

STUDIES = {
    # Status Quo
    'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

    # Extend AL, simple regime
    'rwa-ae-al-4.csv'              : ['AL, 4 days', '#bdd7e7'],
    'rwa-ae-al-5.csv'              : ['AL, 5 days', '#bdd7e7'],

    # Extend AL, more complex regime
    'rwa-ae-al-3-1-1.csv'          : ['AL, 1-day pause, then AL (1 dose)', '#bdd7e7'],
    'rwa-ae-al-3-1-2.csv'          : ['AL, 1-day pause, then AL (2 doses)', '#bdd7e7'],
    'rwa-ae-al-3-2-1.csv'          : ['AL, 2-day pause, then AL (1 dose)', '#bdd7e7'],
    'rwa-ae-al-3-2-2.csv'          : ['AL, 2-day pause, then AL (2 doses)', '#bdd7e7'],
    'rwa-ae-al-3-4-3.csv'          : ['AL, 4 days rest, AL', '#bdd7e7'],

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
    'rwa-rotation-al-3.csv'        : ['DHA-PPQ (3 years) then\nAL (50%) + ASAQ', '#d7b5d8'],
    'rwa-rotation-al-5.csv'        : ['DHA-PPQ (3 years) then\nAL, 5 days (50%) + ASAQ', '#d7b5d8'],
}

EXPERIMENTAL = {
    # Status Quo
    'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

    # Community based health workers follow-up care
    'rwa-ae-al-3-4-3.csv'          : ['AL, 4 days rest, AL', '#bdd7e7'],

    # Sequential Treatments
    'rwa-seq-al-asaq.csv'          : ['AL then ASAQ', '#d7b5d8'],
    'rwa-seq-al-asaq-pause.csv'    : ['AL, 4-day pause, then ASAQ', '#d7b5d8'],

    'rwa-seq-al-dhappq.csv'        : ['AL then DHA-PPQ', '#d7b5d8'],
    'rwa-seq-al-dhappq-pause.csv'  : ['AL, 4-day pause, then DHA-PPQ', '#d7b5d8'],

    'rwa-seq-asaq-al.csv'          : ['ASAQ then AL', '#d7b5d8'],
    'rwa-seq-asaq-al-pause.csv'    : ['ASAQ, 4-day pause, then AL', '#d7b5d8'],
    
    'rwa-seq-dhappq-al.csv'        : ['DHA-PPQ then AL', '#d7b5d8'],
    'rwa-seq-dhappq-al-pause.csv'  : ['DHA-PPQ, 4-day pause, then AL', '#d7b5d8'],    

    # TACT
    'rwa-tact-alaq.csv'            : ['AL + AQ', '#df65b0'],
    'rwa-tact-dhappqmq.csv'        : ['ASMQ + PPQ', '#df65b0'],
}

MANUSCRIPT = {
    # Status Quo
    'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

    # Extend AL, simple regime
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
    'rwa-rotation-al-3.csv'        : ['DHA-PPQ (3 years) then\nAL (50%) + ASAQ', '#d7b5d8'],
    'rwa-rotation-al-5.csv'        : ['DHA-PPQ (3 years) then\nAL, 5 days (50%) + ASAQ', '#d7b5d8'],

    # TACT
    'rwa-tact-alaq.csv'            : ['AL + AQ', '#df65b0'],
    'rwa-tact-dhappqmq.csv'        : ['ASMQ + PPQ', '#df65b0'],
}

DHAPPQ = {
    # Status Quo
    'rwa-pfpr-constant.csv'        : ['Status Quo', '#bdd7e7'],

    # Replace AL
    'rwa-replacement-dhappq.csv'   : ['100% DHA-PPQ', '#6baed6'],

    # AL / DHA-PPQ MFT
    'rwa-mft-al-dhappq-0.25.csv'   : ['AL (75%) + DHA-PPQ (25%)', '#74c476'],
    'rwa-mft-al-dhappq.csv'        : ['AL (50%) + DHA-PPQ (50%)', '#74c476'],
    'rwa-mft-al-dhappq-0.75.csv'   : ['AL (25%) + DHA-PPQ (75%)', '#74c476'],

    # ASAQ / DHA-PPQ MFT
    'rwa-mft-asaq-dhappq-0.25.csv' : ['ASAQ (75%) + DHA-PPQ (25%)', '#31a354'],
    'rwa-mft-asaq-dhappq.csv'      : ['ASAQ (50%) + DHA-PPQ (50%)', '#31a354'],
    'rwa-mft-asaq-dhappq-0.75.csv' : ['ASAQ (25%) + DHA-PPQ (75%)', '#31a354'],

    # Replace AL, 20 years
    'rwa-replacement-dhappq-20y.csv'   : ['100% DHA-PPQ, 20 Years', '#6baed6'],
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

# List of the plots and their mappings
PLOTS = {
    'standard'     : STUDIES,
    'experimental' : EXPERIMENTAL,
    'manuscript'   : MANUSCRIPT,

    'compliance'   : COMPLIANCE,
    'dhappq'       : DHAPPQ,
    'nmcp'         : NMCP
    }

# AL vs 5-day AL treatment genotype report
al_vs_al5 = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-pfpr-constant.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv'
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

# 5-day AL vs DHA-PPQ treatment genotype report
al5_vs_dhappq = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-replacement-dhappq.csv'
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

# 5-day AL vs DHA-PPQ treatment genotype report, with plasmepsin genotype
al5_vs_dhappq_plas = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-replacement-dhappq.csv'
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

# 5-day AL vs DHA-PPQ treatment genotype report, with double resistance data
al5_vs_dhappq_double = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-replacement-dhappq.csv'
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

# 5-day AL vs multiple first-line therapies (MFT) genotype report
al5_vs_mft= {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-mft-asaq-dhappq-0.25.csv'
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

# 5-day AL vs drug cycling treatment genotype report
al5_vs_cycling = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-rotation-al-5.csv'
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

# 5-day AL vs triple-ACT treatment genotype report
al5_vs_tact = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-tact-alaq.csv'
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

# 5-day AL vs AL-ASAQ sequential treatment genotype report
al5_vs_seq_al_asaq = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-seq-al-asaq.csv'
    ],
    'name' : ['AL 5-day', 'AL then ASAQ' ],

    'plot' : ['tf', 'pfpr', 'freq_561h'],
    'left' : ['tf', 'freq_561h'],
    'right' : ['pfpr'],
    'style' : ['-.', '-'],
    'intervention' : 0.41,

    'title' : 'AL 5-day vs. AL then ASAQ',
    'label' : {
        'tf' : '% Treatment Failures',
        'pfpr' : '$\it{Pf}$PR$_{2-10}$',
        'freq_561h' : '561H Frequency',
    }        
}

# 5-day AL vs. AL + DHA-PPQ sequential treatment genotype report
al5_vs_seq_al_dhappq_345 = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-seq-al-dhappq.csv'
    ],
    'name' : ['AL 5-day', 'AL then DHA-PPQ' ],

    'plot' : ['tf', 'pfpr', 'freq_561h'],
    'left' : ['tf', 'freq_561h'],
    'right' : ['pfpr'],
    'style' : ['-.', '-'],
    'intervention' : 0.41,

    'title' : 'AL 5-day vs. AL then DHA-PPQ (345)',
    'label' : {
        'tf' : '% Treatment Failures',
        'pfpr' : '$\it{Pf}$PR$_{2-10}$',
        'freq_561h' : '561H Frequency',
    }        
}

# 5-day AL vs. AL, pause, then DHA-PPQ sequential treatment genotype report
al5_vs_seq_al_dhappq_789 = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-ae-al-5.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-seq-al-dhappq-pause.csv'
    ],
    'name' : ['AL 5-day', 'AL then DHA-PPQ' ],

    'plot' : ['tf', 'pfpr', 'freq_561h'],
    'left' : ['tf', 'freq_561h'],
    'right' : ['pfpr'],
    'style' : ['-.', '-'],
    'intervention' : 0.41,

    'title' : 'AL 5-day vs. AL then DHA-PPQ (789)',
    'label' : {
        'tf' : '% Treatment Failures',
        'pfpr' : '$\it{Pf}$PR$_{2-10}$',
        'freq_561h' : '561H Frequency',
    }        
}

# 5-day AL vs AL-ASAQ sequential treatment genotype report
tact_vs_seq_al_asaq = {
    'source' : [ 
        '../Analysis/ms_data/{}/genotype_dataset/rwa-tact-alaq.csv',
        '../Analysis/ms_data/{}/genotype_dataset/rwa-seq-al-asaq.csv'
    ],
    'name' : ['AL + AQ', 'AL then ASAQ' ],

    'plot' : ['tf', 'pfpr', 'freq_561h'],
    'left' : ['tf', 'freq_561h'],
    'right' : ['pfpr'],
    'style' : ['-.', '-'],
    'intervention' : 0.41,

    'title' : 'AL + AQ vs. AL then ASAQ',
    'label' : {
        'tf' : '% Treatment Failures',
        'pfpr' : '$\it{Pf}$PR$_{2-10}$',
        'freq_561h' : '561H Frequency',
    }        
}