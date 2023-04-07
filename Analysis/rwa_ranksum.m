% rwa_ranksum.m
% 
% Apply the Wilcoxon rank sum test to the various datasets returned to
% calclaute the p-values.
clear;

process(5);
process(0);

% Offset is the number of years from the end of the dataset, so 0 is year 10,
% and 5 is year 5.
function [] = process(offset)
    % Status update
    fprintf('----- Rank Sum vs. Status Quo (Year %d) -----\n', 10 - offset);

    % Every thing is against the status quo
    [sq_failures, sq_frequency] = calculate('ms_data/2024/datasets/rwa-pfpr-constant.csv', offset);
    
    % Iterate overall of the other datasets
    files = dir('ms_data/2024/datasets/rwa-*.csv');
    for ndx = 1:length(files)
        if files(ndx).name == "rwa-561h-verification.csv"
            continue
        end
    
        filename = fullfile(files(ndx).folder, files(ndx).name);
        [failures, frequency] = calculate(filename, offset);
        p_failures = ranksum(sq_failures, failures);
        p_frequency = ranksum(sq_frequency, frequency);
        fprintf('vs. %s; failures: p = %0.4f (log10 = %.2f); frequency: p = %0.4f (log10 = %.2f)\n', ...
            files(ndx).name, p_failures, log10(p_failures), p_frequency, log10(p_frequency));
    end
end

function [failures, frequency] = calculate(filename, offset)
    REPLICATE = 2; DAYSELAPSED = 3; INFECTIONS = 5; WEIGHTED = 9; FAILURES = 11;

    % Read the data, note the unique data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    days = unique(data(:, DAYSELAPSED));

    % Discard everything but the last year
    days = days(end - (11 + 12 * offset):end - (12 * offset));

    % Calcluate the median treatment failures (percentage) and 561H frequency
    failures = []; frequency = [];
    for replicate = replicates
        filtered = data(data(:, REPLICATE) == replicate, :);
        failures = [failures sum(filtered(:, FAILURES))];
        frequency = [frequency sum(filtered(:, WEIGHTED)) / sum(filtered(:, INFECTIONS))];
    end
end