% rwa_basic_stats.m
%
% Calculate the basic statistics for each study, district, etc.
clear;

% Get the frequency data from the files
files = dir('data/datasets/rwa-*.csv');
frequencies = zeros(size(files, 2), 30);
for ndx = 1:length(files)
   filename = fullfile(files(ndx).folder, files(ndx).name);
   report = strcat('out/', strrep(files(ndx).name, '.csv', '.txt'));
   process(filename, report);
end

% Expected file structure
%  1: Configuration Id
%  2: Replicate Id
%  3: Days Elapsed
%  4: District
%  5: Infected Individuals
%  6: Clinical Episodes
%  7: 561H Occurrences
%  8: 561H Clinical Occurrences
%  9: 561H Weighted Occurrences,
% 10: Treatment Failures,
% 11: Genotype Carriers
function [] = process(filename, report)
    REPLICATE = 2; DAYSELAPSED = 3; DISTRICT = 4; INFECTIONS = 5;
    CLINICAL = 6; OCCURRENCES = 9; FAILURES = 10;

    % Load the labels
    labels = readtable('../GIS/rwa_districts.csv');

    % Open the file for writing, note the input file
    out = fopen(report, 'W');
    fprintf(out, '%s\n\n', filename);

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    districts = transpose(unique(data(:, DISTRICT)));

    % Filter on the last 12 months
    days = unique(data(:, DAYSELAPSED));
    days = days(end-11:end);
    data = data(ismember(data(:, DAYSELAPSED), days), :);

    % Find the totals for each replicate, district
    occurrences = zeros(size(replicates, 2), size(districts, 2));
    infections = occurrences;
    clinical = zeros(size(replicates, 2), 1);
    failures = clinical;

    % Calculate the frequency across all replicates, districts
    for ndx = 1:size(replicates, 2)
        for ndy = districts
            filtered = data(data(:, DISTRICT) == ndy, :);
            filtered = filtered(filtered(:, REPLICATE) == replicates(ndx), :);
            occurrences(ndx, ndy) = sum(filtered(:, OCCURRENCES));
            infections(ndx, ndy) = sum(filtered(:, INFECTIONS));
        end
        clinical(ndx) = sum(data(data(:, REPLICATE) == replicates(ndx), CLINICAL));
        failures(ndx) = sum(data(data(:, REPLICATE) == replicates(ndx), FAILURES));
    end
    frequency = occurrences ./ infections;

    % Report the mean and IQR for each district
    for ndy = districts
        fprintf(out, '%s: %.4f (IQR %.4f - %.4f)\n', string(labels{ndy, 2}), prctile(frequency(:, ndy), [50 25 75]));
    end

    % Now calculate the national frequency
    frequency = sum(occurrences, 2) ./ sum(infections, 2);
    fprintf(out, '\nNATIONAL: %.4f (IQR %.4f - %.4f)\n', prctile(frequency, [50 25 75]));
    fprintf(out, 'Clinical: %.2f (IQR %.2f - %.2f\n', prctile(clinical ./ 12, [50 25 75]));
    fprintf(out, 'Failures: %.2f (IQR %.2f - %.2f\n', prctile(failures ./ 12, [50 25 75]));

    % Close the file
    fclose(out);
end

