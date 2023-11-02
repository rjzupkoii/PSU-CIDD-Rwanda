 % rwa_treatment_failures.m
% 
% Calculate the treatment failure for each year supplied.
clear;

calculate('data/datasets/rwa-baseline.csv', 0.25);

function [] = calculate(filename, scaling)
    REPLICATE = 2; DAYSELAPSED = 3; CLINICAL = 6; TREATMENTS = 10; FAILURES = 11;
    YEARS = 12; MODELSTART = '2003-01-01';

    % Read the data
    data = readmatrix(filename);
    replicates = transpose(unique(data(:, REPLICATE)));
    
    % Filter on the dates
    for offset = YEARS:-1:0
        % Filter on the dates
        days = unique(data(:, DAYSELAPSED));
        days = days(end - (11 + 12 * offset):end - (12 * offset));

        year = datestr(datetime(MODELSTART) + days(1), 'yyyy');
        fprintf('\nTimespan: %s - %s (%d months)\n', ...
            datestr(datetime(MODELSTART) + days(1), 'yyyy-mm-dd'), ...
            datestr(datetime(MODELSTART) + days(12), 'yyyy-mm-dd'), ...
            size(days, 1));

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
    
        fprintf('Year: %s | Monthly: %.0f (%.0f - %.0f) | Yearly: %.0f (%.0f - %.0f) | %%: %.2f (%.2f - %.2f)\n', ...
             year, prctile(failures_abs(:), [50 25 75]), prctile(failures_sum(:), [50 25 75]), prctile(failures_prct(:), [50 25 75]));
        fprintf('Year: %s | Clinical: %.0f (IQR: %.0f - %.0f)\n', year, prctile(clinical_sum(:), [50 25 75]))
    end
end