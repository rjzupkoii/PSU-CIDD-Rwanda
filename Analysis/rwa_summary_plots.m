% rwa_summary_plots.m
% 
% When run this script will generate:
% 1) An updated individuial plot for each treatment option
% 2) A summary 'dashboard' plot that allows each option to be viewed
% 3) Summary IQR data as 'out/rwa-iqrs.txt'
%
% NOTE this script should be run after loader.py to ensure that the most 
% recent data has been loaded into data/datasets.
addpath('include');
clear;

% The start date of the simulation
STARTDATE = '2003-01-01';

% The master list of studies that we wish to plot, first value is the index
% of the study in the summary plot
STUDIES = {
    % Status quo
    1, 'data/datasets/rwa-pfpr-constant.csv', 'Status Quo', '', 'plots/rwa-pfpr-constant%s.png';
    3, 'data/datasets/rwa-replacement-asaq.csv', '100% ASAQ Deployment', '2023-01-01', 'plots/rwa-replacement-asaq%s.png';

    % Multiple First-line Therapies
    5, 'data/datasets/rwa-mft-asaq-dhappq.csv', 'MFT ASAQ + DHA-PPQ', '2023-01-01', 'plots/rwa-mft-asaq-dhappq%s.png';
    6, 'data/datasets/rwa-mft-asaq-dhappq-0.25.csv', 'MFT ASAQ (75%) + DHA-PPQ (25%)', '2023-01-01', 'plots/rwa-mft-asaq-dhappq-0.25%s.png';
    7, 'data/datasets/rwa-mft-asaq-dhappq-0.75.csv', 'MFT ASAQ (25%) + DHA-PPQ (75%)', '2023-01-01', 'plots/rwa-mft-asaq-dhappq-0.75%s.png';

    9, 'data/datasets/rwa-mft-al-asaq.csv', 'MFT AL + ASAQ', '2023-01-01', 'plots/rwa-mft-al-asaq%s.png';
    10, 'data/datasets/rwa-mft-al-asaq-0.25.csv', 'MFT AL (75%) + ASAQ (25%)', '2023-01-01', 'plots/rwa-mft-al-asaq-0.25%s.png';
    11, 'data/datasets/rwa-mft-al-asaq-0.75.csv', 'MFT AL (25%) + ASAQ (75%)', '2023-01-01', 'plots/rwa-mft-al-asaq-0.75%s.png';

    13, 'data/datasets/rwa-mft-al-dhappq.csv', 'MFT AL + DHA-PPQ', '2023-01-01', 'plots/rwa-mft-al-dhappq%s.png';
    14, 'data/datasets/rwa-mft-al-dhappq-0.25.csv', 'MFT AL (75%) + DHA-PPQ (25%)', '2023-01-01', 'plots/rwa-mft-al-dhappq-0.25%s.png';
    15, 'data/datasets/rwa-mft-al-dhappq-0.75.csv', 'MFT AL (25%) + DHA-PPQ (75%)', '2023-01-01', 'plots/rwa-mft-al-dhappq-0.75%s.png';

    % Artesunate Extension
    17, 'data/datasets/rwa-ae-al-3-1-1.csv', 'AL 3-1-1', '2023-01-01', 'plots/rwa-ae-al-3-1-1%s.png';
    18, 'data/datasets/rwa-ae-al-3-2-1.csv', 'AL 3-2-1', '2023-01-01', 'plots/rwa-ae-al-3-2-1%s.png';
    19, 'data/datasets/rwa-ae-al-3-1-2.csv', 'AL 3-1-2', '2023-01-01', 'plots/rwa-ae-al-3-1-2%s.png';
    20, 'data/datasets/rwa-ae-al-3-2-2.csv', 'AL 3-2-2', '2023-01-01', 'plots/rwa-ae-al-3-2-2%s.png';
    
    21, 'data/datasets/rwa-ae-al-4.csv', 'AL (Four Days)', '2023-01-01', 'plots/rwa-ae-al-4%s.png';
    23, 'data/datasets/rwa-ae-al-5.csv', 'AL (Five Days)', '2023-01-01', 'plots/rwa-ae-al-5%s.png';
};

% Make sure our directories exist
warning('off', 'MATLAB:MKDIR:DirectoryExists');
mkdir('plots/summary');

% Generate a single 561H validation plot with IQR
disp('Generating 561H spike verification plot...')
rwa_intervention_plot('data/datasets/rwa-561h-verification.csv', '561H Verification', STARTDATE, '', 'plots/rwa-561h-verification.png');

% Generate all of the informative plots and summaries
rwa_frequency_plots(STARTDATE, STUDIES);

% Generate all of the type plots
rwa_data_plots(STARTDATE, STUDIES, 'infections');
rwa_data_plots(STARTDATE, STUDIES, 'occurrences');
rwa_data_plots(STARTDATE, STUDIES, 'treatmentfailure');
