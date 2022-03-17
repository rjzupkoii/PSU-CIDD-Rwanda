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

% The population adjustment applied to the simuation
ADJUSTMENT = 0.25;

% The number of years to generate the plots for
YEARS = NaN;

% The master list of studies that we wish to plot, first value is the index
% of the study in the summary plot
STUDIES = {
    % Status quo
    1, 'data/datasets/rwa-pfpr-constant.csv', 'Status Quo', '', 'plots/rwa-pfpr-constant%s.png';

    % Rotations
    3, 'data/datasets/rwa-rotation-al-3.csv', 'Rotate DHA-PPQ (3yr), MFT AL (50%) + ASAQ (50%)', '2023-01-01', 'plots/rwa-rotation-al-3%s.png';
    4, 'data/datasets/rwa-rotation-al-5.csv', 'Rotate DHA-PPQ (3yr), MFT AL 5 day (50%) + ASAQ (50%)', '2023-01-01', 'plots/rwa-rotation-al-5%s.png';

    % Multiple First-line Therapies
    5, 'data/datasets/rwa-mft-asaq-dhappq-0.25.csv', 'MFT ASAQ (75%) + DHA-PPQ (25%)', '2023-01-01', 'plots/rwa-mft-asaq-dhappq-0.25%s.png';
    6, 'data/datasets/rwa-mft-asaq-dhappq.csv', 'MFT (50%) ASAQ + DHA-PPQ (50%)', '2023-01-01', 'plots/rwa-mft-asaq-dhappq%s.png';
    7, 'data/datasets/rwa-mft-asaq-dhappq-0.75.csv', 'MFT ASAQ (25%) + DHA-PPQ (75%)', '2023-01-01', 'plots/rwa-mft-asaq-dhappq-0.75%s.png';
    8, 'data/datasets/rwa-replacement-dhappq.csv', '100% DHA-PPQ Deployment', '2023-01-01', 'plots/rwa-replacement-dhappq%s.png';
    
    9, 'data/datasets/rwa-mft-al-asaq-0.25.csv', 'MFT AL (75%) + ASAQ (25%)', '2023-01-01', 'plots/rwa-mft-al-asaq-0.25%s.png';
    10, 'data/datasets/rwa-mft-al-asaq.csv', 'MFT AL (50%) + ASAQ (50%)', '2023-01-01', 'plots/rwa-mft-al-asaq%s.png';
    11, 'data/datasets/rwa-mft-al-asaq-0.75.csv', 'MFT AL (25%) + ASAQ (75%)', '2023-01-01', 'plots/rwa-mft-al-asaq-0.75%s.png';
    12, 'data/datasets/rwa-replacement-asaq.csv', '100% ASAQ Deployment', '2023-01-01', 'plots/rwa-replacement-asaq%s.png';

    13, 'data/datasets/rwa-mft-al-dhappq-0.25.csv', 'MFT AL (75%) + DHA-PPQ (25%)', '2023-01-01', 'plots/rwa-mft-al-dhappq-0.25%s.png';
    14, 'data/datasets/rwa-mft-al-dhappq.csv', 'MFT AL (50%) + DHA-PPQ (50%)', '2023-01-01', 'plots/rwa-mft-al-dhappq%s.png';
    15, 'data/datasets/rwa-mft-al-dhappq-0.75.csv', 'MFT AL (25%) + DHA-PPQ (75%)', '2023-01-01', 'plots/rwa-mft-al-dhappq-0.75%s.png';

    % Artesunate Extension
    17, 'data/datasets/rwa-ae-al-4.csv', 'AL (Four Days)', '2023-01-01', 'plots/rwa-ae-al-4%s.png';
    18, 'data/datasets/rwa-ae-al-5.csv', 'AL (Five Days)', '2023-01-01', 'plots/rwa-ae-al-5%s.png';
    19, 'data/datasets/rwa-ae-al-3-1-1.csv', 'AL 3-1-1', '2023-01-01', 'plots/rwa-ae-al-3-1-1%s.png';
    20, 'data/datasets/rwa-ae-al-3-2-1.csv', 'AL 3-2-1', '2023-01-01', 'plots/rwa-ae-al-3-2-1%s.png';
   
    21, 'data/datasets/rwa-ae-al-3-1-2.csv', 'AL 3-1-2', '2023-01-01', 'plots/rwa-ae-al-3-1-2%s.png';
    22, 'data/datasets/rwa-ae-al-3-2-2.csv', 'AL 3-2-2', '2023-01-01', 'plots/rwa-ae-al-3-2-2%s.png';

    % Triple-ACT
    23, 'data/datasets/rwa-tact-alaq.csv', 'TACT AL+AQ', '2023-01-01', 'plots/rwa-tact-alaq-2%s.png';
    24, 'data/datasets/rwa-tact-dhappqmq.csv', 'TACT DHA-PPQ + MQ', '2023-01-01', 'plots/rwa-tact-dhappqmq-2%s.png';
};

% Make sure our directories exist
warning('off', 'MATLAB:MKDIR:DirectoryExists');
mkdir('out');
mkdir('plots/summary');

% Generate a single 561H validation plot with IQR
if isnan(YEARS)
    disp('Generating 561H spike verification plot...')
    rwa_data_plot('561H', 1, 'data/datasets/rwa-561h-verification.csv', '561H Verification', STARTDATE, '', 'plots/rwa-561h-verification.png');
end

% Generate all of the informative plots and summaries
generate_rwa_plots('561H', STARTDATE, ADJUSTMENT, STUDIES, YEARS);

% Generate all of the type plots
generate_rwa_plots('clinical', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
generate_rwa_plots('infections', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
generate_rwa_plots('occurrences', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
generate_rwa_plots('weighted', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
generate_rwa_plots('treatmentfailure', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
generate_rwa_plots('genotypecarriers', STARTDATE, ADJUSTMENT, STUDIES, YEARS);
