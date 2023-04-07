% rwa_frequency.m
% 
% Calculate the 561H frequency for the the last 11 years of the study.
clear;

calculate('ms_data/2024/datasets/rwa-pfpr-constant.csv');

function [] = calculate(filename)
    REPLICATE = 2; DAYSELAPSED = 3; INFECTIONS = 5; WEIGHTED = 9;
    YEARS = 12; ENDPOINT = 2035;

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    
    % Filter on the dates
    for offset = YEARS:-1:0
        % Filter on the dates
        days = unique(data(:, DAYSELAPSED));
        days = days(end - (11 + 12 * offset):end - (12 * offset));
        filtered = data(ismember(data(:, DAYSELAPSED), days), :);
    
        % Get the values for each replicate
        frequency = zeros(size(replicates, 2), 1);
        for ndx = 1:size(replicates, 2)
            frequency(ndx) = (sum(filtered(filtered(:, REPLICATE) == replicates(ndx), WEIGHTED)) / sum(filtered(filtered(:, REPLICATE) == replicates(ndx), INFECTIONS)));
        end
    
        fprintf('Year: %d | 561H: %.2f (%.2f - %.2f)\n', ENDPOINT - offset, prctile(frequency(:), [50 25 75]));
    end
end