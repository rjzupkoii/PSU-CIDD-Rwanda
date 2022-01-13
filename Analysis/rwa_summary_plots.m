% rwa_summary_plots.m
% 
% When run this script will generate:
% 1) An updated individuial plot for each treatment option
% 2) A summary 'dashboard' plot that allows each option to be viewed
% 3) Summary IQR data as 'out/rwa-iqrs.txt'
%
% NOTE this script should be run after loader.py to ensure that the most 
% recent data has been loaded into data/datasets.
clear;

% The start date of the simulation
STARTDATE = '2003-01-01';

% The master list of studies that we wish to plot, first value is the index
% of the study in the summary plot
STUDIES = {
    % Status quo
    1, 'data/datasets/rwa-pfpr-constant.csv', 'Status Quo', '', 'plots/rwa-pfpr-constant.png';

    % Multiple First-line Therapies
    4, 'data/datasets/rwa-mft-asaq-dhappq.csv', 'MFT ASAQ + DHA-PPQ', '2023-01-01', 'plots/rwa-mft-asaq-dhappq.png';

    % Artesunate Extension
    7, 'data/datasets/rwa-ae-al-3-1-1.csv', 'AL 3-1-1', '2023-01-01', 'plots/rwa-ae-al-3-1-1.png';
    8, 'data/datasets/rwa-ae-al-4.csv', 'AL (Four Days)', '2023-01-01', 'plots/rwa-ae-al-4.png';
    9, 'data/datasets/rwa-ae-al-5.csv', 'AL (Five Days)', '2023-01-01', 'plots/rwa-ae-al-5.png';
};

% Generate the single plots and store the values returned in cell arrays
results = {};
frequencies = {};
for ndx = 1:size(STUDIES, 1)
    [results{end + 1}, frequencies{end + 1}] = rwa_intervention_plot(STUDIES{ndx, 2}, STUDIES{ndx, 3}, STARTDATE, STUDIES{ndx, 4}, STUDIES{ndx, 5});
end

% Write the summary results to the out file
writecell(transpose(results), 'out/rwa-iqrs.txt', 'Delimiter', 'space');

% Load the dates, these should all be the same throughout the data sets
raw = readmatrix(STUDIES{1, 2});
dates = unique(raw(:, 3)) + datenum(STARTDATE);

% Generate the summary plot with the data sets
ylimit = 0;
for ndx = 1:size(STUDIES, 1)
    % Find the 75th percentile and the y-limit
    values = quantile(frequencies{ndx}, 0.75);
    ylimit = max(ylimit, max(values));

    % Add the subplot
    subplot(4, 3, STUDIES{ndx, 1});
    hold on;
    title(results{ndx});
    plot(dates, values, 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(frequencies{ndx}), 'black');
    plot(dates, quantile(frequencies{ndx}, 0.25), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
end

% Wrap up the formatting of the subplots
for ndx = 1:size(STUDIES, 1)
    subplot(4, 3, STUDIES{ndx, 1});
    ylim([0 ylimit]);
    xlim([min(dates) max(dates)]);
    datetick('x', 'yyyy', 'keepticks', 'keeplimits');
end