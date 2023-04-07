 % rwa_treatment_failures.m
% 
% Calculate the treatment failure for the last 11 years of the study.
clear;

calculate('ms_data/2024/datasets/rwa-ae-al-3-4-3.csv', 0.25);

function [] = calculate(filename, scaling)
    REPLICATE = 2; DAYSELAPSED = 3; CLINICAL = 6; TREATMENTS = 10; FAILURES = 11;
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
    
        % Prepare our data 
        failures_abs = zeros(size(replicates, 2), 1);
        failures_prct = zeros(size(replicates, 2), 1);
        failures_sum = zeros(size(replicates, 2), 1);
        clinical_sum = zeros(size(replicates, 2), 1);
    
        % Get the values for each replicate
        for ndx = 1:size(replicates, 2)
            temp = filtered(filtered(:, REPLICATE) == replicates(ndx), :);
            failures_abs(ndx) = sum(temp(:, FAILURES) / scaling) / 12;                            % Monthly average
            failures_prct(ndx) = (sum(temp(:, FAILURES)) / sum(temp(:, TREATMENTS))) * 100.0;     % Annual percentage
            failures_sum(ndx) = sum(temp(:, FAILURES) / scaling);                                 % Sum for year
            clinical_sum(ndx) = sum(temp(:, CLINICAL) / scaling);
        end
    
         fprintf('Year: %d | Monthly: %.0f (%.0f - %.0f) | Yearly: %.0f (%.0f - %.0f) | %%: %.2f (%.2f - %.2f)\n', ...
             ENDPOINT - offset, prctile(failures_abs(:), [50 25 75]), prctile(failures_sum(:), [50 25 75]), prctile(failures_prct(:), [50 25 75]));
        fprintf('Year: %d | Clinical: %.0f (IQR: %.0f - %.0f)\n', ENDPOINT - offset, prctile(clinical_sum(:), [50 25 75]))
    end
end