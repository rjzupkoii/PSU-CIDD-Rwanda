% rwa_ranksum.m
% 
% Apply the Wilcoxon rank sum test to the various datasets returned to
% calclaute the p-values. The values calculated are as follows:
% failures (sum) - annual sum of treatment failures
% failures (monthly) - monthly average of treatment failures
% failures (percent) - annual percentage of treatment failures (total failures / total treatments)
% freqeuncy - 561H frequency in the last month of the comparsion period
clear;

file = fopen('rwa_ranksum.txt', 'w');
process(5, file);
fprintf(file, '\n\n');
process(0, file);
fclose(file);

% Offset is the number of years from the end of the dataset, so 0 is year 10,
% and 5 is year 5.
function [] = process(offset, file)
    % Status update
    fprintf(file, '----- Rank Sum vs. Status Quo (Year %d) -----\n', 10 - offset);

    % Every thing is against the status quo
    [sq_failures, sq_percent_failures, sq_frequency] = calculate('ms_data/2024/datasets/rwa-pfpr-constant.csv', offset);
    sq_percent_failures_monthly = sq_failures / 12;
    
    % Iterate overall of the other datasets
    files = dir('ms_data/2024/datasets/rwa-*.csv');
    for ndx = 1:length(files)
        if files(ndx).name == "rwa-561h-verification.csv"
            continue
        end
    
        filename = fullfile(files(ndx).folder, files(ndx).name);
        [failures, percent_failures, frequency] = calculate(filename, offset);
        p_failures_sum = ranksum(sq_failures, failures);
        p_failures_monthly = ranksum(sq_percent_failures_monthly, failures / 12);
        p_percent_failures = ranksum(sq_percent_failures, percent_failures);
        p_frequency = ranksum(sq_frequency, frequency);
        fprintf(file, ['vs. %s\n\tfailures, sum: p = %0.4f (log10 = %.2f); ' ...
                               'monthly: p = %0.4f (log10 = %.2f); ' ...
                               'precent: p = %0.4f (log10 = %.2f)\n' ...
                               '\tfrequency: p = %0.4f (log10 = %.2f)\n'], ...
                files(ndx).name, ...
                p_failures_sum, log10(p_failures_sum), ...
                p_failures_monthly, log10(p_failures_monthly), ...
                p_percent_failures, log10(p_percent_failures), ...
                p_frequency, log10(p_frequency));
    end
end

function [failures, percent_failures, frequency] = calculate(filename, offset)
    REPLICATE = 2; DAYSELAPSED = 3; INFECTIONS = 5; WEIGHTED = 9; TREATMENTS = 10; FAILURES = 11;

    % Read the data, note the unique data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    days = unique(data(:, DAYSELAPSED));

    % Discard everything but the last year
    days = days(end - (11 + 12 * offset):end - (12 * offset));

    % Calcluate the median treatment failures (percentage) and 561H frequency
    failures = []; percent_failures = []; frequency = [];
    for replicate = replicates
        % Calculate total treatment failures for the year
        filtered = data(data(:, REPLICATE) == replicate & ismember(data(:, DAYSELAPSED), days), :);
        failures = [failures sum(filtered(:, FAILURES))];

        % Calculate the annual percent treatment failures
        percent_failures = [percent_failures sum(filtered(:, FAILURES)) / sum(filtered(:, TREATMENTS))];

        % Calcluate the 561H frequency for the last month of the year
        filtered = data(data(:, REPLICATE) == replicate & data(:, DAYSELAPSED) == days(12), :);
        frequency = [frequency sum(filtered(:, WEIGHTED)) / sum(filtered(:, INFECTIONS))];
    end
end