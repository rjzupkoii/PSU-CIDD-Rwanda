function [result, data] = rwa_data_plot(type, adjustment, dataFilename, intervention, startDate, interventionDate, imageFilename)
    % Generate a single data plot for an intervention.
    
    % Load the data and the unique datas
    raw = readmatrix(dataFilename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the national sums / frequency
    [column, divisor, label] = parse_type(type);
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
        iqr = prctile(mean(data(:, end - 11:end), 2) / divisor, [25 50 75]);
        result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(2), iqr(1), iqr(3));
    else
        postfix = 'total';
        if divisor == 12
            postfix = 'per month';
        end

        % IQR over the total data points of the last year, per replicate
        value = quantile(sum(data(:, end - 11:end), 2) / divisor, 0.5);
        if log10(value) >= 6
            result = sprintf("%s: %.2fM %s", intervention, value / 10^6, postfix);
        else
            result = sprintf("%s: %.1fK %s", intervention, value / 10^3, postfix);
        end
        data = log10(data);
    end

    % Plot the data
    fig = figure;
    set(fig, 'Visible', 'off');
    hold on;
    dates = dates + datenum(startDate);
    plot(dates, quantile(data, 0.90), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(data), 'black');
    plot(dates, quantile(data, 0.05), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    if interventionDate ~= ""
        xline(datenum(interventionDate), '-', intervention);
    end
    
    % Format, save, and close the plot
    format_plot(type, result, label);
    save_plot(sprintf(imageFilename, strcat('-', type)));
end
