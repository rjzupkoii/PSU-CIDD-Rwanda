% rwa_basic_stats.m
%
% Calculate the basic statistics for the 561H frequency, clinical cases,
% and treatment failures for each study, district, etc. as a CSV file with 
% 3-, 5-, and 10-year end-points for the returned data sets.
%
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
clear;

PATH = 'ms_data/2024/datasets/';
generate_reports(PATH, 0.25);

function [] = generate_reports(path, scaling)
    ENDPOINTS = 'out/rwa-endpoints.csv';
    
    % Open the endpoints for output
    output = fopen(ENDPOINTS, 'W');
    
    % Add the header to the file
    fprintf(output, 'Study,Three Years,,,,,Five Years,,,,,Ten Years,,,,,\n');
    fprintf(output, '%s,\n', repmat(',Clinical Cases,Treatments,Treatment Failures,Treatment Failures,561H Frequency', 1, 3));
    
    % Get the frequency data from the files
    files = dir(strcat(path, 'rwa-*.csv'));
    for ndx = 1:length(files)
        if files(ndx).name == "rwa-561h-verification.csv"
            continue
        end
    
        filename = fullfile(files(ndx).folder, files(ndx).name);
        summary(filename, scaling, strcat('out/', strrep(files(ndx).name, '.csv', '.txt')));
        endpoints(filename, scaling, strrep(files(ndx).name, '.csv', ''), output);
    end
    
    % Close the file
    fclose(output);
end

function [] = endpoints(filename, scaling, study, output) 
    REPLICATE = 2; DAYSELAPSED = 3;
    INFECTIONS = 5; CLINICAL = 6; OCCURRENCES = 9; TREATMENTS = 10; FAILURES = 11;
    
    % We have 11 years of data following intervention, but only care about
    % T+3, T+5, and T+10 years post intervention.
    OFFSETS = [8, 6, 1];

    % Note the filename
    fprintf(output, '%s,', study);

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));

    for offset = OFFSETS
        % Filter on the dates
        days = unique(data(:, DAYSELAPSED));
        days = days(end - (11 + 12 * offset):end - (12 * offset));
        filtered = data(ismember(data(:, DAYSELAPSED), days), :);
        
        % Prepare our data 
        cases = zeros(size(replicates, 2), 1);
        treatments = zeros(size(replicates, 2), 1);
        failures_abs = zeros(size(replicates, 2), 1);
        failures_prct = zeros(size(replicates, 2), 1);
        frequency = zeros(size(replicates, 2), 1);

        % Get the values for each replicate
        for ndx = 1:size(replicates, 2)
            temp = filtered(filtered(:, REPLICATE) == replicates(ndx), :);
            cases(ndx) = sum(temp(:, CLINICAL) / scaling) / 12;                                   % Monthly average
            treatments(ndx) = sum(temp(:, TREATMENTS) / scaling) / 12;                            % Monthly average
            failures_abs(ndx) = sum(temp(:, FAILURES) / scaling) / 12;                            % Monthly average
            failures_prct(ndx) = (sum(temp(:, FAILURES)) / sum(temp(:, TREATMENTS))) * 100.0;     % Annual percentage
            frequency(ndx) = sum(temp(:, OCCURRENCES)) / sum(temp(:, INFECTIONS));                % Annual frequency
        end

        % Write the data points
        fprintf(output, '%.0f (%.0f - %.0f),', prctile(cases(:), [50 25 75]));
        fprintf(output, '%.0f (%.0f - %.0f),', prctile(treatments(:), [50 25 75]));
        fprintf(output, '%.0f (%.0f - %.0f),', prctile(failures_abs(:), [50 25 75]));
        fprintf(output, '%.2f (%.2f - %.2f),', prctile(failures_prct(:), [50 25 75]));
        fprintf(output, '%.2f (%.2f - %.2f),', prctile(frequency(:), [50 25 75]));
    end

    % End the line we are on
    fprintf(output, '\n');
end

function [] = summary(filename, scaling, report)
    REPLICATE = 2; DAYSELAPSED = 3; DISTRICT = 4; INFECTIONS = 5;
    CLINICAL = 6; OCCURRENCES = 9; FAILURES = 11;

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
        clinical(ndx) = sum(data(data(:, REPLICATE) == replicates(ndx), CLINICAL) / scaling);
        failures(ndx) = sum(data(data(:, REPLICATE) == replicates(ndx), FAILURES) / scaling);
    end
    frequency = occurrences ./ infections;

    % Report the mean and IQR for each district
    for ndy = districts
        fprintf(out, '%s: %.4f (IQR %.4f - %.4f)\n', string(labels{ndy, 2}), prctile(frequency(:, ndy), [50 25 75]));
    end

    % Now calculate the national frequency
    frequency = sum(occurrences, 2) ./ sum(infections, 2);
    fprintf(out, '\nNATIONAL: %.4f (%.4f - %.4f)\n', prctile(frequency, [50 25 75]));
    fprintf(out, 'Clinical: %.2f (%.2f - %.2f)\n', prctile(clinical ./ 12, [50 25 75]));
    fprintf(out, 'Failures: %.2f (%.2f - %.2f)\n'    , prctile(failures ./ 12, [50 25 75]));

    % Close the file
    fclose(out);
end

