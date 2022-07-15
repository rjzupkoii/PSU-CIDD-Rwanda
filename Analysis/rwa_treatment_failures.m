% rwa_treatment_failures.m
% 
% Calculate the treatment failure for the last 11 years of the study.
clear;

calculate('data/datasets/rwa-pfpr-constant.csv');

function [] = calculate(filename)
    REPLICATE = 2; DAYSELAPSED = 3; TREATMENTS = 10; FAILURES = 11;

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    
    % Filter on the dates
    for offset = 10:-1:0
        % Filter on the dates
        days = unique(data(:, DAYSELAPSED));
        days = days(end - (11 + 12 * offset):end - (12 * offset));
        filtered = data(ismember(data(:, DAYSELAPSED), days), :);
    
        % Prepare our data 
        failures_abs = zeros(size(replicates, 2), 1);
        failures_prct = zeros(size(replicates, 2), 1);
        failures_sum = zeros(size(replicates, 2), 1);
    
        % Get the values for each replicate
        for ndx = 1:size(replicates, 2)
            temp = filtered(filtered(:, REPLICATE) == replicates(ndx), :);
            failures_abs(ndx) = sum(temp(:, FAILURES)) / 12;                                      % Monthly average
            failures_prct(ndx) = (sum(temp(:, FAILURES)) / sum(temp(:, TREATMENTS))) * 100.0;     % Annual percentage
            failures_sum(ndx) = sum(temp(:, FAILURES));                                           % Sum for year
        end
    
        fprintf('Year: %d | Monthly: %.0f (%.0f - %.0f) | Yearly: %.0f (%.0f - %.0f) | %%: %.2f (%.2f - %.2f)\n', ...
            10 - offset, prctile(failures_abs(:), [50 25 75]), prctile(failures_sum(:), [50 25 75]), prctile(failures_prct(:), [50 25 75]));
    end
end