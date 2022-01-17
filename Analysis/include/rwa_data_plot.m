function [result, data] = rwa_data_plot(type, dataFilename, intervention, startDate, interventionDate, imageFilename)
    % Generate a single data plot for an intervention.
   
    % Parse out the type of intervention we are looking at
    if strcmp(type, 'infections')
        column = 5;
        label = 'P. falciparum infected indivdiuals (log_{10})';
    elseif strcmp(type, 'occurrences')
        column = 7;
        label = '561H Occurrences (log_{10})';
    elseif strcmp(type, 'treatmentfailure')
        column = 10;
        label = 'Treatment Failures (log_{10})';
    else
        error('Unknown data type: %s', type);
    end
    
    % Load the data and the unique datas
    raw = readmatrix(dataFilename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the national sums, convert to log10
    data = zeros(size(dates, 2), size(replicates, 2));
    for ndx = 1:size(replicates, 1)
        filtred = raw(raw(:, 2) == replicates(ndx), :);
        for ndy = 1:size(dates, 1)
            data(ndx, ndy) = sum(filtred(filtred(:, 3) == dates(ndy), column));
        end
    end
    data = log10(data);
    
    % Note the median and IQR of the last year
    iqr = prctile(data(:, end - 11:end), [25 50 70]);
    result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(2), iqr(1), iqr(3));

    % Plot the data
    fig = figure;
    set(fig, 'Visible', 'off');
    hold on;
    dates = dates + datenum(startDate);
    plot(dates, quantile(data, 0.75), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(data), 'black');
    plot(dates, quantile(data, 0.25), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    if interventionDate ~= ""
        xline(datenum(interventionDate), '-', intervention);
    end
    
    % Format, save, and close the plot
    format_plot(result, label);
    save_plot(sprintf(imageFilename, strcat('-', type)));
end
