% rwa_frequency.m
% 
% Calculate the 561H frequency for the the last 11 years of the study.
clear;

calculate('2003-01-01', 'data/datasets/rwa-baseline.csv');

function [] = calculate(model_start, filename)
    REPLICATE = 2; DAYSELAPSED = 3; INFECTIONS = 5; WEIGHTED = 9;
    YEARS = 12;

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    
    % Filter on the dates
    for offset = YEARS:-1:0
        % Filter on the dates
        days = unique(data(:, DAYSELAPSED));
        days = days(end - (11 + 12 * offset):end - (12 * offset));
        filtered = data(data(:, DAYSELAPSED) == days(12), :);
    
        % Get the values for each replicate
        frequency = zeros(size(replicates, 2), 1);
        for ndx = 1:size(replicates, 2)
            frequency(ndx) = (sum(filtered(filtered(:, REPLICATE) == replicates(ndx), WEIGHTED)) / sum(filtered(filtered(:, REPLICATE) == replicates(ndx), INFECTIONS)));
        end
    
        fprintf('%s | 561H: %.2f (%.2f - %.2f)\n', ...
            datestr(datetime(model_start) + days(12), 'yyyy-mm-dd'), ...
            prctile(frequency(:), [50 25 75]));
    end
end