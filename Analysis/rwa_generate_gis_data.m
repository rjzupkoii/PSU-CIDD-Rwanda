% rwa_generate_gis_data.m
%
% Use the verification data file to generate an aggregated CSV file that
% can be used in ArcGIS Pro to plot projected cases for Rwanda.
clear;

data = readmatrix('data/10825-verification-data.csv');

% Get the data for 2017, assuming end date is 2025-01-01

dates = unique(data(:, 1));
data = data(data(:, 1) >= dates(end - 96), :);       % 2017-01-01
data = data(data(:, 1) < dates(end - 84), :);       % 2018-01-01

results = zeros(30, 4);
for ndx = 1:30
    results(ndx, 1) = ndx;                                  % District 
    results(ndx, 2) = max(data(data(:, 2) == ndx, 3));      % Population
    results(ndx, 3) = sum(data(data(:, 2) == ndx, 4));      % Clinical
    results(ndx, 4) = sum(data(data(:, 2) == ndx, 5));      % Treated
end

writematrix(results, 'rwa-verification.csv');