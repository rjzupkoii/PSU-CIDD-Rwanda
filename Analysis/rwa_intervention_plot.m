% rwa_summary_plot.m
%
% Generate a summary plot of the treatment interventions.
clear;

STARTDATE = '2003-01-01';

[result, frequencies] = process('data/datasets/rwa-ae-al-3-1-1.csv', 'AL 3-1-1', STARTDATE, '2023-01-01');

function [result, frequencies] = process(filename, intervention, startDate, interventionDate)
    % Load the data and the unique datas
    raw = readmatrix(filename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the frequency for each block of dates
    frequencies = zeros(size(dates, 2), size(replicates, 2));
    for ndx = 1:size(replicates, 1)
        data = raw(raw(:, 2) == replicates(ndx), :);
        for ndy = 1:size(dates, 1)
            frequencies(ndx, ndy) = sum(data(data(:, 3) == dates(ndy), 9)) / sum(data(data(:, 3) == dates(ndy), 5));
        end
    end
    
    % Note the median and IQR of the last month
    iqr = prctile(frequencies(:, end), [25 50 70]);
    result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(1), iqr(2), iqr(3));
    
    % Plot the intervention data
    hold on;
    dates = dates + datenum(startDate);
    plot(dates, quantile(frequencies, 0.75), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(frequencies), 'black');
    plot(dates, quantile(frequencies, 0.25), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    xline(datenum(interventionDate), '-', 'AL 3-1-1 Introduction');
    
    % Finish the plot
    title(result);
    xlabel('Model Year');
    ylabel('561H Frequency');
    datetick('x', 'yyyy');
end

