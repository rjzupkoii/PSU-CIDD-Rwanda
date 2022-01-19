function [result, data] = rwa_data_plot(type, adjustment, dataFilename, intervention, startDate, interventionDate, imageFilename)
    % Generate a single data plot for an intervention.
    
    % Load the data and the unique datas
    raw = readmatrix(dataFilename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the national sums / frequency
    [column, label] = parse_type(type);
    data = zeros(size(dates, 2), size(replicates, 2));
    for ndx = 1:size(replicates, 1)
        filtred = raw(raw(:, 2) == replicates(ndx), :);
        for ndy = 1:size(dates, 1)
            if strcmp(type, '561H')
                data(ndx, ndy) = sum(filtred(filtred(:, 3) == dates(ndy), 9)) / sum(filtred(filtred(:, 3) == dates(ndy), 5));
            else
                data(ndx, ndy) = sum(filtred(filtred(:, 3) == dates(ndy), column)) / adjustment;
            end
        end
    end
    
    % Cast the data and prepare the plot title as dictated by the type
    if strcmp(type, '561H')
        % IQR over the mean last year 561H frequency, per replicate
        iqr = prctile(mean(data(:, end - 11:end), 2), [25 50 75]);
        result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(2), iqr(1), iqr(3));
    else
        jf = java.text.DecimalFormat;
        % IQR over the total data points of the last year, per replicate
        iqr = prctile(sum(data(:, end - 11:end), 2), [25 50 75]);
        result = sprintf("%s: %s (IQR %s - %s)", intervention, ...
            jf.format(iqr(2)), jf.format(iqr(1)), jf.format(iqr(3)));
        data = log10(data);
    end

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
    format_plot(type, result, label);
    save_plot(sprintf(imageFilename, strcat('-', type)));
end
